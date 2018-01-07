$ = jQuery;

$(document).ready(function() {
  var display = $(".hide-text").hide(),
  current = 0;
  display.eq(0).show();
  function showNext() {
    if (current < display.length - 1) {
      display.eq(current).delay(1000).fadeOut('fast', function() {
        current++;
        display.eq(current).fadeIn('fast');
        showNext();
      });
    }
  }
  setTimeout(function() { showNext(); }, 1000);
  
  //front page header show and hide
  var height = $(".top-content .backstretch").height();
  $(window).scroll(function(){
    if($(this).scrollTop() > height)
    {
      $('.header-section').show();
      $(".fornt-page-section").addClass("front-page-search");
    }
    else
    {
      $('.header-section').hide();
      $(".fornt-page-section").removeClass("front-page-search");
    }
  });
});

$(document).ready(function() {
  $(".video").click(function() {
    $.fancybox({
      'padding'       : 0,
      'autoScale'     : false,
      'transitionIn'  : 'none',
      'transitionOut' : 'none',
      'title'         : this.title,
      'width'         : 640,
      'height'        : 385,
      'href'          : this.href.replace(new RegExp("watch\\?v=", "i"), 'v/'),
      'type'          : 'swf',
      'swf'           : {
        'wmode'             : 'transparent',
        'allowfullscreen'   : 'true'
      }
    });
    return false;
  });
});

$(function() {
$('a[href*=#]:not([href=#])').click(function() {
  if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
    var target = $(this.hash);
    target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
    if (target.length) {
      $('html,body').animate({
        scrollTop: target.offset().top
      }, 500);
      return false;
    }
  }
});
});
$('.newsCard-parent').mouseover(
function () {
  $(this).find('.newsread-more-link').css({
    display: 'block'
  });
  $(this).find('.newsread-more-link').animate({
    bottom: '0px',
    background: '#ccc'
  }, 300);
});
$('.newsCard-parent').mouseout(
function () {
    $('.newsread-more-link').css({
      display: 'none'
    });
});

$(window).load(function() {
  $(".fbajax").html('<div id="fb-root"></div><script>(function(d, s, id) {var js, fjs = d.getElementsByTagName(s)[0];if (d.getElementById(id)) return;js = d.createElement(s); js.id = id;js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.4&appId=1526470804243594";fjs.parentNode.insertBefore(js, fjs);}(document, "script", "facebook-jssdk"));</script><div class="fb-page" data-href="https://www.facebook.com/sociofuzz" data-width="300"data-height="300" data-small-header="false" data-adapt-container-width="true" data-hide-cover="false" data-show-facepile="false" data-show-posts="true"><div class="fb-xfbml-parse-ignore"><blockquote cite="https://www.facebook.com/sociofuzz"><a href="https://www.facebook.com/sociofuzz">SocioFuzz</a></blockquote></div></div>');
  // $(".fblike").html('<div class="fb-page" data-href="https://www.facebook.com/sociofuzz" data-width="300" data-hide-cover="false" data-show-facepile="false" data-show-posts="false"></div>')
  $(".twitterajax").html('<a class="twitter-timeline" href="https://twitter.com/sociofuzz" data-widget-id="632804674408546304">Tweets by @sociofuzz</a><script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?"http":"https";if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>')
});



$.ajax({
  url: '/headerSearch',
  type: 'POST',
  dataType: 'html',
  data: $(this).serialize(),
  success: function(newContent){
    header = JSON.parse(newContent);
    var source = header.head 
    $(".tags").autocomplete({
      source: source,
      select: function( event, ui ) { 
        url = "/movie/"+ ui.item.value;
        window.location = url;
      }
    });
  }
});