from app.core.knowledge.html_extractor import extract_main_text


SAMPLE_HTML = """
<html>
  <head><title>Doc Title</title></head>
  <body>
    <nav>Home Products Support</nav>
    <div class="cookie-banner">Accept cookies</div>
    <main class="post-document">
      <h1>Quarantined Files</h1>
      <p>Use the Falcon console to review removed malware and quarantined files.</p>
      <p>Filter by host, severity, and remediation action.</p>
    </main>
    <footer>Copyright CrowdStrike</footer>
  </body>
</html>
"""


def test_extract_main_text_strips_chrome_and_keeps_article():
    text = extract_main_text(SAMPLE_HTML)

    assert "Quarantined Files" in text
    assert "removed malware" in text
    assert "Accept cookies" not in text
    assert "Copyright CrowdStrike" not in text
    assert "Home Products Support" not in text
