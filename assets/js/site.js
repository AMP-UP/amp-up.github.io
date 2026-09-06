(function() {
  var navigation = [
    { href: 'index.html', label: 'Home', page: 'index' },
    { href: 'who.html', label: 'Who We Are', page: 'who' },
    { href: 'mentorship.html', label: 'What We Do', page: 'mentorship' },
    { href: 'resources.html', label: 'Resources', page: 'resources' },
    { href: 'https://docs.google.com/forms/d/e/1FAIpQLSfnKzRmQcijnV6SJhno3CJpGVL9L43WxYj08SBRozsKXL7kYg/viewform', label: 'Apply', page: 'apply', buttonClass: 'button primary', external: true }
  ];

  function getCurrentPage() {
    var bodyPage = document.body && document.body.getAttribute('data-page');
    if (bodyPage) {
      return bodyPage;
    }

    var path = window.location.pathname.split('/').pop() || 'index.html';
    var match = path.replace(/\.(html|htm)$/i, '');
    return match || 'index';
  }

  function buildHeaderMarkup(currentPage) {
    var listItems = navigation.map(function(item) {
      var classes = item.page === currentPage ? 'current' : '';
      var linkClass = item.buttonClass ? ' class="' + item.buttonClass + '"' : '';
      var attrs = item.external ? ' target="_blank" rel="noopener noreferrer"' : '';
      return '<li class="' + classes + '"><a href="' + item.href + '"' + linkClass + attrs + '>' + item.label + '</a></li>';
    }).join('');

    var headerClass = currentPage === 'index' ? 'alt' : '';
    var logoMarkup = currentPage === 'index'
      ? '<div id="logoimg" aria-hidden="true"></div>'
      : '<img src="images/Logo2_color_black.png" alt="AMP-UP logo" style="float:left; margin-top:-10px; margin-bottom:-10px; width:50px;" />';

    return [
      '<header id="header" class="' + headerClass + '">',
      '  <h1 id="logo"><a href="index.html">' + logoMarkup + '</a></h1>',
      '  <nav id="nav" aria-label="Main navigation">',
      '    <ul>',
      '      ' + listItems,
      '    </ul>',
      '  </nav>',
      '</header>'
    ].join('\n');
  }

  function buildFooterMarkup() {
    return [
      '<footer id="footer">',
      '  <ul class="copyright">',
      '    <li>&copy; AMP-UP</li><li>Design: <a href="http://html5up.net">HTML5 UP</a></li>',
      '  </ul>',
      '</footer>'
    ].join('\n');
  }

  function applyLogoFix() {
    var style = document.createElement('style');
    style.textContent = [
      'header.special .icon {',
      '  position: static !important;',
      '  display: block !important;',
      '  width: min(60vw, 420px) !important;',
      '  height: auto !important;',
      '  margin: 0 auto 1.25em !important;',
      '  left: auto !important;',
      '  top: auto !important;',
      '  float: none !important;',
      '  text-align: center !important;',
      '}',
      'header.special .icon img, .site-brand-image {',
      '  display: block !important;',
      '  width: min(60vw, 420px) !important;',
      '  max-width: 100% !important;',
      '  height: auto !important;',
      '  margin: 0 auto 1.25em !important;',
      '  position: relative !important;',
      '}',
      '@media screen and (max-width: 736px) {',
      '  header.special .icon, header.special .icon img, .site-brand-image {',
      '    width: min(82vw, 290px) !important;',
      '  }',
      '}'
    ].join('\n');
    document.head.appendChild(style);
  }

  function hydrateShell() {
    var headerTarget = document.getElementById('site-header');
    var footerTarget = document.getElementById('site-footer');
    var currentPage = getCurrentPage();

    if (headerTarget) {
      headerTarget.innerHTML = buildHeaderMarkup(currentPage);
    }

    if (footerTarget) {
      footerTarget.innerHTML = buildFooterMarkup();
    }
  }

  hydrateShell();
  applyLogoFix();
})();
