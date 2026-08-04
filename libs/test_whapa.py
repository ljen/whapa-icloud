#!/usr/bin/python3
"""
test_whapa.py - Pruebas de humo de WhaPa 2.00

Uso:  python3 doc/test_whapa.py

Crea bases de datos de prueba que reproducen los esquemas de Android e iOS y
comprueba que cada herramienta hace su trabajo. No necesita material real.
"""

import os
import sqlite3
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "libs"))

import whacipher
import whacodes as codes
import whareader as reader
import whareport as report


def _db_android(path, n=60):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_system(message_row_id INT, action_type INT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);""")
    for i in range(1, n + 1):
        con.execute(
            "INSERT INTO message VALUES (?,?,?,?,?,?,?,?,?)",
            (
                i,
                1,
                i % 2,
                "K" * 32,
                1,
                1700000000000 + i * 1000,
                0 if i % 3 else 66,
                "t%d" % i,
                1 if i == 5 else 0,
            ),
        )
    con.execute("INSERT INTO message_system VALUES (3,12)")
    con.commit()
    con.close()


def _db_ios(path, n=60):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE ZWACHATSESSION(Z_PK INTEGER PRIMARY KEY, ZCONTACTJID TEXT, ZPARTNERNAME TEXT);
    CREATE TABLE ZWAMESSAGE(Z_PK INTEGER PRIMARY KEY, ZCHATSESSION INT, ZISFROMME INT,
      ZGROUPMEMBER INT, ZMESSAGEDATE REAL, ZMESSAGETYPE INT, ZTEXT TEXT,
      ZSTANZAID TEXT, ZSTARRED INT, ZFROMJID TEXT, ZMEDIAITEM INT);
    INSERT INTO ZWACHATSESSION VALUES (1,'34600111222@s.whatsapp.net','Juan');""")
    for i in range(1, n + 1):
        con.execute(
            "INSERT INTO ZWAMESSAGE VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                i,
                1,
                i % 2,
                None,
                721692800 + i * 60,
                0 if i % 3 else 46,
                "t%d" % i,
                "5E" + "0" * 18,
                0,
                None,
                None,
            ),
        )
    con.commit()
    con.close()


def test_codigos():
    assert codes.kind_of(codes.ANDROID, 66) is codes.Kind.POLL
    assert codes.kind_of(codes.IOS, 46) is codes.Kind.POLL
    assert codes.kind_of(codes.ANDROID, 112) is codes.Kind.ADVANCED_PRIVACY
    assert codes.is_deleted(codes.ANDROID, 64) and codes.is_deleted(codes.IOS, 14)
    assert codes.kind_of(codes.ANDROID, 99999) is codes.Kind.UNKNOWN
    assert "comunidad" in codes.system_action_description(12).lower()
    print("  whacodes: catalogo de codigos OK")


def test_cipher():
    d = tempfile.mkdtemp()
    src = os.path.join(d, "a.db")
    _db_android(src, 5)
    original = open(src, "rb").read()
    clave = "aa" * 32
    enc, dec = os.path.join(d, "a.crypt15"), os.path.join(d, "b.db")
    whacipher.encrypt(src, clave, enc)
    cab = whacipher.parse_header(open(enc, "rb").read())
    assert cab["version"] == "crypt15" and len(cab["iv"]) == 16
    whacipher.decrypt(enc, clave, dec)
    assert open(dec, "rb").read() == original
    print("  whacipher: crypt15 ida y vuelta byte a byte OK")


def test_lector():
    d = tempfile.mkdtemp()
    for nombre, crea, plat in (
        ("msgstore.db", _db_android, codes.ANDROID),
        ("ChatStorage.sqlite", _db_ios, codes.IOS),
    ):
        p = os.path.join(d, nombre)
        crea(p)
        assert reader.detect_platform(p) == plat
        ext = reader.read(p)
        s = ext.summary()
        assert s["total"] == 60 and s["chats"] == 1
        assert len(ext.source_files[0]["sha256"]) == 64
        print(f"  whareader: {plat} detectado y leido OK")


def test_filtros_e_informes():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "msgstore.db")
    _db_android(p)
    ext = reader.read(p)

    assert len(report.search(ext, report.Filter(text="t7"))) == 1
    assert len(report.search(ext, report.Filter(text="T7", case_sensitive=True))) == 0
    assert len(report.search(ext, report.Filter(text=r"^t[12]$", regex=True))) == 2
    assert len(report.search(ext, report.Filter(text="t", whole_word=True))) == 0
    assert len(report.search(ext, report.Filter(raw_types={66}))) == 20
    assert len(report.search(ext, report.Filter(only_starred=True))) == 1
    env = len(report.search(ext, report.Filter(direction="sent")))
    rec = len(report.search(ext, report.Filter(direction="received")))
    sis = len(report.search(ext, report.Filter(direction="system")))
    # the fixture includes a system message, which is neither sent nor received
    assert sis == 1 and env + rec + sis == 60
    assert report.Filter().is_empty()
    print("  whareport: motor de filtrado OK")

    # interactive report: initial HTML should not grow with messages
    tam = []
    for n in (50, 5000):
        q = os.path.join(d, "m%d.db" % n)
        _db_android(q, n)
        r = report.build_report(reader.read(q), os.path.join(d, "r%d" % n))
        tam.append(r["shell_size"])
    assert abs(tam[0] - tam[1]) < 2000, "el HTML inicial crece con los mensajes"
    print("  whareport: informe interactivo de tamano constante OK")

    # languages
    for lang, marca in (("ES", ">Buscar</button>"), ("EN", ">Search</button>")):
        r = report.build_report(ext, os.path.join(d, "l" + lang), lang=lang)
        assert marca in open(r["path"], encoding="utf-8").read()
    print("  whareport: informe en ES y EN OK")

    # printable with documented criteria
    flt = report.Filter(text="t1", direction="sent")
    out = os.path.join(d, "print.html")
    r = report.build_printable(ext, out, flt=flt, case_ref="REF-1", max_messages=999)
    cuerpo = open(out, encoding="utf-8").read()
    assert "<script" not in cuerpo, "el imprimible no debe llevar JavaScript"
    assert "@page" in cuerpo and "Criterios de selección" in cuerpo
    assert "«t1»" in cuerpo and "REF-1" in cuerpo
    assert r["selected"] == r["messages"]
    print("  whareport: informe imprimible con criterios OK")

    # interactive report respects filter
    r1 = report.build_report(ext, os.path.join(d, "sf"))
    r2 = report.build_report(
        ext, os.path.join(d, "cf"), flt=report.Filter(raw_types={66})
    )
    assert r2["pages"] <= r1["pages"]
    print("  whareport: el informe interactivo respeta el filtro OK")

    # CSV
    hits = report.search(ext, report.Filter(text="t1"))
    csvp = os.path.join(d, "h.csv")
    report.export_csv(hits, csvp)
    cuerpo = open(csvp, encoding="utf-8-sig").read()
    assert cuerpo.startswith("n;chat;chat_jid;fecha_utc")
    assert len(cuerpo.strip().split("\n")) == len(hits) + 1
    print("  whareport: exportacion CSV OK")


def test_adjuntos():
    """Si se aporta la carpeta WhatsApp, el informe debe enlazar los archivos."""
    import struct
    import wave
    import zlib

    d = tempfile.mkdtemp()
    wa = os.path.join(d, "WhatsApp")
    os.makedirs(os.path.join(wa, "Media", "WhatsApp Images"))
    os.makedirs(os.path.join(wa, "Media", "WhatsApp Audio"))

    img = os.path.join(wa, "Media", "WhatsApp Images", "IMG-1.jpg")
    raw = b"".join(b"\x00" + bytes((0, 168, 132)) * 4 for _ in range(4))

    def ch(t, x):
        c = t + x
        return (
            struct.pack(">I", len(x))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    open(img, "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
        + ch(b"IDAT", zlib.compress(raw))
        + ch(b"IEND", b"")
    )
    aud = os.path.join(wa, "Media", "WhatsApp Audio", "AUD-1.wav")
    with wave.open(aud, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x01" * 400)

    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_media(message_row_id INT, chat_row_id INT, file_path TEXT,
      mime_type TEXT, file_size INT, media_caption TEXT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',1,1705300000000,1,NULL,0);
    INSERT INTO message VALUES (2,1,1,'K',NULL,1705300100000,2,NULL,0);
    INSERT INTO message VALUES (3,1,0,'K',1,1705300200000,1,NULL,0);""")
    # absolute path of the terminal, relative path, and one that does not exist
    con.executemany(
        "INSERT INTO message_media VALUES (?,?,?,?,?,?)",
        [
            (
                1,
                1,
                "/storage/emulated/0/WhatsApp/Media/WhatsApp Images/IMG-1.jpg",
                "image/jpeg",
                72,
                None,
            ),
            (2, 1, "Media/WhatsApp Audio/AUD-1.wav", "audio/wav", 844, None),
            (
                3,
                1,
                "/storage/emulated/0/WhatsApp/Media/WhatsApp Images/NO-EXISTE.jpg",
                "image/jpeg",
                0,
                None,
            ),
        ],
    )
    con.commit()
    con.close()

    ext = reader.read(db)

    # no folder: nothing is located, but the report is generated the same
    r0 = report.build_report(ext, os.path.join(d, "sin"))
    assert r0["media_found"] == 0

    # with folder and copy: 2 of 3 located
    r1 = report.build_report(
        ext, os.path.join(d, "con"), media_root=wa, copy_media=True
    )
    assert r1["media_found"] == 2 and r1["media_missing"] == 1, r1
    copiados = os.listdir(os.path.join(d, "con", "media"))
    assert "IMG-1.jpg" in copiados and "AUD-1.wav" in copiados

    # the attachment data travels in the report data file
    datos = open(
        os.path.join(d, "con", "data", "c0000_p0000.js"), encoding="utf-8"
    ).read()
    assert "media/IMG-1.jpg" in datos and "media/AUD-1.wav" in datos

    # The printable embeds the thumbnail and records the original route
    out = os.path.join(d, "print.html")
    report.build_printable(ext, out, media_root=wa, copy_media=True, max_messages=99)
    cuerpo = open(out, encoding="utf-8").read()
    assert 'class="thumb"' in cuerpo
    assert "Ruta en la base" in cuerpo and "archivo no localizado" in cuerpo

    # the viewer knows how to paint each type
    assert "function mediaHtml" in report.JS and "<audio controls" in report.JS
    print("  whareport: adjuntos localizados, copiados y enlazados OK")


def test_ubicaciones():
    """Ubicaciones: bloque en el visor, KML valido y sin llamadas remotas."""
    import xml.etree.ElementTree as ET

    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_location(message_row_id INT, chat_row_id INT,
      latitude REAL, longitude REAL);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',1,1705300000000,5,NULL,0);
    INSERT INTO message VALUES (2,1,1,'K',NULL,1705300100000,16,NULL,0);
    INSERT INTO message VALUES (3,1,0,'K',1,1705300200000,0,'sin ubicacion',0);
    INSERT INTO message_location VALUES (1,1,36.72016,-4.42034);
    INSERT INTO message_location VALUES (2,1,40.41678,-3.70379);""")
    con.commit()
    con.close()

    ext = reader.read(db)
    conubi = [m for m in ext.messages if m.latitude is not None]
    assert len(conubi) == 2

    # filter by location
    assert len(report.search(ext, report.Filter(only_location=True))) == 2

    # Valid KML and with the two coordinates
    kml = os.path.join(d, "loc.kml")
    n = report.export_kml(report.search(ext, report.Filter(only_location=True)), kml)
    assert n == 2
    raiz = ET.parse(kml).getroot()
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    marcas = raiz.findall(".//k:Placemark", ns)
    assert len(marcas) == 2
    coords = [m.find(".//k:coordinates", ns).text for m in marcas]
    assert "-4.42034,36.72016,0" in coords, coords  # KML is lon,lat
    assert marcas[0].find(".//k:when", ns) is not None

    # without locations nothing is invented
    assert (
        report.export_kml(
            report.search(ext, report.Filter(text="sin ubicacion")),
            os.path.join(d, "vacio.kml"),
        )
        == 0
    )

    # the viewer paints the block and does NOT link remote images
    r = report.build_report(ext, os.path.join(d, "rep"))
    assert "function locHtml" in report.JS
    assert "openstreetmap.org" in report.JS and "google.com/maps" in report.JS
    datos = open(
        os.path.join(d, "rep", "data", "c0000_p0000.js"), encoding="utf-8"
    ).read()
    assert "36.72016" in datos
    cuerpo = open(r["path"], encoding="utf-8").read()
    assert "staticmap" not in cuerpo, "el informe no debe pedir mapas al abrirse"
    assert 'src="http' not in cuerpo, "no debe haber recursos remotos en el HTML"
    print("  whareport: ubicaciones, KML y sin llamadas remotas OK")


def test_whachat_informes():
    """whachat debe generar los mismos informes que whapa."""
    import whachat

    d = tempfile.mkdtemp()
    chat = os.path.join(d, "Chat de WhatsApp con Juan.txt")
    open(chat, "w", encoding="utf-8").write(
        "25/8/20, 19:52:23 - Los mensajes y las llamadas estan cifrados de extremo a extremo.\n"
        "25/8/20, 19:52:30 - Juan Perez: Buenas\n"
        "25/8/20, 19:53:01 - Yo: te paso la foto\n"
        "25/8/20, 19:53:15 - Yo: IMG-1.jpg (archivo adjunto)\n"
        "25/8/20, 19:55:10 - Juan Perez: PTT-1.opus (archivo adjunto)\n"
    )
    # attachments next to the chat, as exported by WhatsApp
    import struct
    import wave
    import zlib

    raw = b"".join(b"\x00" + bytes((0, 168, 132)) * 4 for _ in range(4))

    def ch(t, x):
        c = t + x
        return (
            struct.pack(">I", len(x))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    open(os.path.join(d, "IMG-1.jpg"), "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
        + ch(b"IDAT", zlib.compress(raw))
        + ch(b"IEND", b"")
    )
    with wave.open(os.path.join(d, "PTT-1.opus"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x01" * 200)

    df = whachat.getDataFrame(chat, "android")
    assert len(df) == 5

    ext = whachat.to_extraction(
        df, "Yo", "%d/%m/%y %H:%M:%S", "android", chat_name="Juan", source_file=chat
    )
    assert len(ext.messages) == 5
    tipos = {m.kind.value for m in ext.messages}
    assert "image" in tipos and "audio" in tipos and "system" in tipos
    # dates resolved even if the mask is not exact
    ext2 = whachat.to_extraction(df, "Yo", "%d/%m/%Y %H:%M", "android")
    assert all(m.timestamp for m in ext2.messages), "las fechas deben resolverse igual"
    # address
    assert sum(1 for m in ext.messages if m.from_me) == 2
    # verification of origin
    assert len(ext.source_files[0]["sha256"]) == 64

    salida = os.path.join(d, "rep")
    hechos = whachat.informes(
        ext,
        salida,
        media_root=d,
        copy_media=True,
        interactivo=True,
        imprimible=True,
        csv_out=True,
    )
    clases = {c for c, _ in hechos}
    assert clases == {"interactivo", "imprimible", "csv"}
    for c, r in hechos:
        assert os.path.exists(r["path"])
        if c != "csv":
            assert r["media_found"] == 2, (c, r)
    # the interactive report is the same engine
    cuerpo = open(os.path.join(salida, "report", "index.html"), encoding="utf-8").read()
    assert "function runSearch" in cuerpo and "function mediaHtml" in cuerpo
    print("  whachat: mismos informes que whapa OK")


def test_consola_segura():
    """Imprimir emojis no debe abortar la herramienta (consola cp1252)."""
    import io

    import whadeps

    TXT = "mensaje con emoji \U0001f42d y acentos <<Bartolo>>"

    class FakeTTY(io.TextIOWrapper):
        def isatty(self):
            return True

    orig = sys.stdout
    try:
        # real cp1252 console: the coding is preserved, what does not fit is replaced
        buf = io.BytesIO()
        sys.stdout = FakeTTY(buf, encoding="cp1252", errors="strict")
        whadeps.safe_console()
        print(TXT)
        sys.stdout.flush()
        salida = buf.getvalue().decode("cp1252")
        assert "Bartolo" in salida and "acentos" in salida

        # Piped output: Full UTF-8, emoji included
        buf2 = io.BytesIO()
        sys.stdout = io.TextIOWrapper(buf2, encoding="cp1252", errors="strict")
        whadeps.safe_console()
        print(TXT)
        sys.stdout.flush()
        assert "\U0001f42d" in buf2.getvalue().decode("utf-8")
    finally:
        sys.stdout = orig
    print("  consola: los emojis ya no abortan la ejecucion OK")


def test_lid():
    """Los identificadores LID no deben mostrarse como si fueran telefonos."""
    d = tempfile.mkdtemp()
    p = os.path.join(d, "m.db")
    con = sqlite3.connect(p)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'120363000000@g.us');
    INSERT INTO jid VALUES (2,'233749350498426@lid');
    INSERT INTO jid VALUES (3,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',2,1762844892000,0,'hola',0);""")
    con.commit()
    con.close()

    # no correspondence table: marked as LID
    ext = reader.read(p)
    assert ext.messages[0].sender == "LID:233749350498426", ext.messages[0].sender

    # with table: translates to the phone
    con = sqlite3.connect(p)
    con.executescript("""
    CREATE TABLE lid_jid_map(lid_row_id INT, jid_row_id INT);
    INSERT INTO lid_jid_map VALUES (2,3);""")
    con.commit()
    con.close()
    ext = reader.read(p)
    assert ext.messages[0].sender == "34600111222", ext.messages[0].sender
    print("  LID: marcado sin correspondencia y traducido con ella OK")


def test_nombre_de_grupo():
    """Un grupo debe mostrar su nombre, no su identificador."""
    d = tempfile.mkdtemp()
    p = os.path.join(d, "m.db")
    con = sqlite3.connect(p)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT, subject TEXT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'120363000000@g.us');
    INSERT INTO jid VALUES (2,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1,'Grupo de trabajo');
    INSERT INTO chat VALUES (2,2,NULL);
    INSERT INTO message VALUES (1,1,0,'K',2,1762844892000,0,'hola',0);
    INSERT INTO message VALUES (2,2,0,'K',2,1762844992000,0,'privado',0);""")
    con.commit()
    con.close()

    ext = reader.read(p)
    chats = {c.chat_id: c for c in ext.chats()}
    grupo = chats["120363000000@g.us"]
    assert grupo.name == "Grupo de trabajo", grupo.name
    assert grupo.is_group
    # The individual chat has no subject: it falls to the number
    individual = chats["34600111222@s.whatsapp.net"]
    assert individual.label == "34600111222"
    assert not individual.is_group
    print("  nombre de grupo resuelto desde chat.subject OK")


def test_salida_por_defecto():
    """Sin -o, el informe nunca debe acabar dentro de libs/."""
    import subprocess

    raiz = RAIZ
    libs = os.path.join(raiz, "libs")
    d = tempfile.mkdtemp()
    db = os.path.join(d, "m.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',1,1700000000000,0,'hola',0);""")
    con.commit()
    con.close()

    # running from libs/, the report should go up to the root
    antes = os.path.exists(os.path.join(libs, "report"))
    r = subprocess.run(
        [sys.executable, os.path.join(libs, "whapa.py"), db, "-m", "-a", "-r", "ES"],
        cwd=libs,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert not os.path.exists(os.path.join(libs, "report")) or antes, (
        "el informe no debe crearse dentro de libs/"
    )
    generado = os.path.join(raiz, "report")
    assert os.path.exists(generado), r.stdout
    import shutil

    shutil.rmtree(generado, ignore_errors=True)

    # from any work folder, it stays there
    trabajo = tempfile.mkdtemp()
    r = subprocess.run(
        [sys.executable, os.path.join(libs, "whapa.py"), db, "-m", "-a", "-r", "ES"],
        cwd=trabajo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert os.path.exists(os.path.join(trabajo, "report")), r.stdout
    print("  salida por defecto: nunca dentro de libs/ OK")


def test_nombres_de_contacto():
    """Los chats deben mostrar el nombre, tambien cuando van por LID."""
    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT, subject TEXT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE lid_jid_map(lid_row_id INT, jid_row_id INT);
    INSERT INTO jid VALUES (1,'17064475537618@lid');
    INSERT INTO jid VALUES (2,'34600111222@s.whatsapp.net');
    INSERT INTO jid VALUES (3,'92028381708365@lid');
    INSERT INTO jid VALUES (4,'34611222333@s.whatsapp.net');
    INSERT INTO lid_jid_map VALUES (1,2);
    INSERT INTO chat VALUES (1,1,NULL),(2,3,NULL),(3,4,NULL);
    INSERT INTO message VALUES (1,1,0,'K',1,1700000000000,0,'a',0);
    INSERT INTO message VALUES (2,2,0,'K',3,1700000100000,0,'b',0);
    INSERT INTO message VALUES (3,3,0,'K',4,1700000200000,0,'c',0);""")
    con.commit()
    con.close()

    wa = os.path.join(d, "wa.db")
    con = sqlite3.connect(wa)
    con.execute("""CREATE TABLE wa_contacts(jid TEXT, display_name TEXT,
                   wa_name TEXT, given_name TEXT, nickname TEXT,
                   sort_name TEXT, number TEXT, status TEXT)""")
    con.executemany(
        "INSERT INTO wa_contacts VALUES (?,?,?,?,?,?,?,?)",
        [
            # in the phone book
            (
                "34600111222@s.whatsapp.net",
                "Juan Perez",
                None,
                None,
                None,
                None,
                "+34 600 111 222",
                None,
            ),
            # NOT in the agenda: the name is only in wa_name
            (
                "34611222333@s.whatsapp.net",
                None,
                "Maria (WhatsApp)",
                None,
                None,
                None,
                "+34611222333",
                None,
            ),
        ],
    )
    con.commit()
    con.close()

    ext = reader.read(db, wa_db=wa)
    chats = {c.chat_id: c.label for c in ext.chats()}

    # LID with equivalence: resolves to the address book name
    assert chats["17064475537618@lid"] == "Juan Perez", chats
    # LID without equivalence: it is dialed, it is not impersonated by telephone
    assert chats["92028381708365@lid"] == "LID:92028381708365", chats
    # name only in wa_name (not in the phonebook): also shown
    assert chats["34611222333@s.whatsapp.net"] == "Maria (WhatsApp)", chats

    # search by number even if the format does not match
    ct = ext.buscar_contacto("34600111222@s.whatsapp.net")
    assert ct and ct.display_name == "Juan Perez"

    # without wa.db, no names are invented
    ext2 = reader.read(db)
    chats2 = {c.chat_id: c.label for c in ext2.chats()}
    assert chats2["34611222333@s.whatsapp.net"] == "34611222333"
    print("  contactos: LID resuelto, wa_name usado y numeros comparados OK")


def test_remitente_en_grupo():
    """En un grupo, el remitente debe salir con nombre si esta en la agenda."""
    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT, subject TEXT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'120363999@g.us'),(2,'34616362926@s.whatsapp.net'),
                           (3,'34699888777@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1,'Grupo');
    INSERT INTO message VALUES (1,1,0,'K',2,1700000000000,0,'a',0);
    INSERT INTO message VALUES (2,1,0,'K',3,1700000100000,0,'b',0);
    INSERT INTO message VALUES (3,1,0,'K',2,1700000200000,116,NULL,0);""")
    con.commit()
    con.close()

    wa = os.path.join(d, "wa.db")
    con = sqlite3.connect(wa)
    con.execute("""CREATE TABLE wa_contacts(jid TEXT, display_name TEXT,
                   wa_name TEXT, number TEXT)""")
    con.execute(
        "INSERT INTO wa_contacts VALUES "
        "('34616362926@s.whatsapp.net','Paco',NULL,'+34 616 362 926')"
    )
    con.commit()
    con.close()

    ext = reader.read(db, wa_db=wa)
    por_id = {m.row_id: m for m in ext.messages}
    assert por_id[1].sender_name == "Paco"
    assert por_id[1].sender == "34616362926", "el numero original no se pierde"
    assert por_id[1].sender_label == "Paco"
    # no contact: the number stays, nothing is invented
    assert por_id[2].sender_name is None
    assert por_id[2].sender_label == "34699888777"

    # The report shows name and number
    out = os.path.join(d, "p.html")
    report.build_printable(ext, out, max_messages=99)
    cuerpo = open(out, encoding="utf-8").read()
    assert "Paco (34616362926)" in cuerpo

    # The CSV separates number and name
    csvp = os.path.join(d, "h.csv")
    report.export_csv(report.search(ext, report.Filter()), csvp)
    lineas = open(csvp, encoding="utf-8-sig").read().splitlines()
    assert "nombre_remitente" in lineas[0]
    assert "Paco" in lineas[1]

    # uncatalogued types are not lost or broken
    desconocidos = [m for m in ext.messages if m.kind is codes.Kind.UNKNOWN]
    assert len(desconocidos) == 1 and desconocidos[0].raw_type == 116
    assert "116" in desconocidos[0].type_desc
    print("  remitente de grupo con nombre y tipos sin catalogar OK")


def test_texto_danado():
    """Un texto con bytes invalidos no debe abortar el analisis."""
    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT, subject TEXT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1,NULL);
    INSERT INTO message VALUES (1,1,0,'K',1,1700000000000,0,'sano con acentos aei',0);""")
    # emoji cut in half, saved as TEXT
    con.execute(
        "INSERT INTO message(_id,chat_row_id,from_me,key_id,"
        "sender_jid_row_id,timestamp,message_type,starred) "
        "VALUES (2,1,0,'K',1,1700000100000,0,0)"
    )
    con.execute(
        "UPDATE message SET text_data = CAST(? AS TEXT) WHERE _id=2",
        (sqlite3.Binary(b"Todav\xc3\xada le cambio el nombre \xf0\x9f\x98"),),
    )
    # value saved as BLOB in a text column
    con.execute(
        "INSERT INTO message VALUES (3,1,0,'K',1,1700000200000,0,?,0)",
        (sqlite3.Binary(b"otro \xff\xfe roto"),),
    )
    con.commit()
    con.close()

    ext = reader.read(db)  # should not throw exception
    assert len(ext.messages) == 3
    assert ext.damaged_text >= 1, "deberia contar el texto danado"

    por_id = {m.row_id: m for m in ext.messages}
    # what is legible is preserved; only what is broken is marked
    assert "Todav" in por_id[2].text and "cambio el nombre" in por_id[2].text
    assert "\ufffd" in por_id[2].text
    # the BLOB arrives as text, not bytes
    assert isinstance(por_id[3].text, str)
    assert "otro" in por_id[3].text and "roto" in por_id[3].text

    # and the reports are generated without problem
    out = os.path.join(d, "p.html")
    report.build_printable(ext, out, max_messages=99)
    assert "cambio el nombre" in open(out, encoding="utf-8").read()
    report.export_csv(report.search(ext, report.Filter()), os.path.join(d, "h.csv"))
    print("  texto danado: no aborta y se conserva lo legible OK")


def test_estado_de_lectura():
    """Estado de entrega y lectura, incluidos los recibos de grupo."""
    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT, subject TEXT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT, status INT, received_timestamp INT,
      receipt_server_timestamp INT);
    CREATE TABLE receipt_user(_id INTEGER PRIMARY KEY, message_row_id INT,
      receipt_user_jid_row_id INT, receipt_timestamp INT, read_timestamp INT,
      played_timestamp INT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net'),(2,'120363999@g.us');
    INSERT INTO chat VALUES (1,1,NULL),(2,2,'Grupo');
    INSERT INTO message VALUES (1,1,1,'K',NULL,1700000000000,0,'leido',0,13,NULL,NULL);
    INSERT INTO message VALUES (2,1,1,'K',NULL,1700000100000,0,'entregado',0,5,NULL,NULL);
    INSERT INTO message VALUES (3,1,0,'K',1,1700000200000,0,'recibido',0,0,NULL,NULL);
    INSERT INTO message VALUES (4,2,1,'K',NULL,1700000300000,0,'grupo',0,5,NULL,NULL);
    INSERT INTO receipt_user VALUES (1,4,1,1700000301000,1700000302000,NULL);
    INSERT INTO receipt_user VALUES (2,4,1,1700000301000,0,NULL);""")
    con.commit()
    con.close()

    ext = reader.read(db)
    por_id = {m.row_id: m for m in ext.messages}

    # The same code means different things depending on whether it is sent or received.
    assert "Leido" in por_id[1].status_desc and por_id[1].leido
    assert "Entregado" in por_id[2].status_desc and not por_id[2].leido
    assert "Recibido" in por_id[3].status_desc
    assert codes.status_description(0, True) != codes.status_description(0, False)

    # in group: count how many received and how many read
    assert por_id[4].delivered_to == 2 and por_id[4].read_by == 1
    assert por_id[4].leido, "si alguien lo leyo, consta como leido"

    # complementary filters
    leidos = report.search(ext, report.Filter(only_read=True))
    sin = report.search(ext, report.Filter(only_unread=True))
    assert len(leidos) + len(sin) == len(ext.messages)
    assert not report.Filter(only_read=True).is_empty()

    # appears in the printable and in the CSV
    out = os.path.join(d, "p.html")
    report.build_printable(ext, out, max_messages=99)
    cuerpo = open(out, encoding="utf-8").read()
    assert "Estado:" in cuerpo and "entregado a 2, leido por 1" in cuerpo
    csvp = os.path.join(d, "h.csv")
    report.export_csv(report.search(ext, report.Filter()), csvp)
    cab = open(csvp, encoding="utf-8-sig").read().splitlines()[0]
    for col in ("estado", "leido", "entregado_a", "leido_por"):
        assert col in cab
    print("  estado de entrega y lectura, tambien en grupos OK")


def test_gui_segura():
    gui = os.path.join(RAIZ, "whapa-gui.py")
    fuente = open(gui, encoding="utf-8").read()
    import ast

    arbol = ast.parse(fuente)
    # The tree is analyzed, not the text: the mention in the comment does not count
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute):
            llamada = "{}.{}".format(getattr(nodo.func.value, "id", ""), nodo.func.attr)
            assert llamada not in ("os.system", "os.popen"), (
                "la interfaz no debe lanzar ordenes con " + llamada
            )
    assert "subprocess.Popen" in fuente
    trabajo = fuente[fuente.index("def _work(self, argv):") :]
    for malo in ("filedialog.", "messagebox.", ".get()", "self.after("):
        assert malo not in trabajo, (
            "acceso inseguro a Tk en el hilo de trabajo: " + malo
        )
    print("  whapa-gui: sin os.system y sin tocar Tk desde el hilo de trabajo OK")


def test_sin_apis_obsoletas():
    import pathlib

    for f in pathlib.Path(os.path.join(RAIZ, "libs")).glob("wha*.py"):
        src = f.read_text(encoding="utf-8", errors="replace")
        assert "utcnow(" not in src, f"{f.name}: utcnow() obsoleto"
    assert sys.version_info >= (3, 11), "se requiere Python 3.11 o superior"
    print("  compatibilidad con Python 3.11+ OK")


if __name__ == "__main__":
    print("Pruebas de humo de WhaPa 2.00\n")
    test_codigos()
    test_cipher()
    test_lector()
    test_filtros_e_informes()
    test_adjuntos()
    test_ubicaciones()
    test_whachat_informes()
    test_consola_segura()
    test_lid()
    test_nombre_de_grupo()
    test_salida_por_defecto()
    test_nombres_de_contacto()
    test_remitente_en_grupo()
    test_texto_danado()
    test_estado_de_lectura()
    test_gui_segura()
    test_sin_apis_obsoletas()
    print("\nTodas las pruebas han pasado.")
