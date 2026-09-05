(function() {
  var navigation = [
    { href: 'index.html', label: 'Home', page: 'index' },
    { href: 'who.html', label: 'Who We Are', page: 'who' },
    { href: 'mentorship.html', label: 'What We Do', page: 'mentorship' },
    { href: 'resources.html', label: 'Resources', page: 'resources' }
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
      return '<li class="' + classes + '"><a href="' + item.href + '">' + item.label + '</a></li>';
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
      '      <li><a href="https://docs.google.com/forms/d/e/1FAIpQLSfnKzRmQcijnV6SJhno3CJpGVL9L43WxYj08SBRozsKXL7kYg/viewform" class="button primary">Apply</a></li>',
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hydrateShell);
  } else {
    hydrateShell();
  }
})();
