$ = jQuery;
$(document).ready(function() {
  $(".fancybox1").click(function() {
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
function onPlayerReady(event) {
  event.target.playVideo();
}
function onPlayerStateChange(event) {
  if (event.data === 0) {
    $.fancybox.next();
  }
}

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

$(document).ready(function() {
  $('.tab-class').click(function( ) {
  $('.tab-class').removeClass('active');
  $(this).addClass('active')
});

if ($(window).width() > 767) {
  $(".part").hide();
  $(".part1").show();    
  $('.nav-tab').click(function() {
    $('.nav-tab').removeClass('active');
    $(this).addClass('active');
    var id = $(this).attr('data'); 
    $(".part").hide();
    $("." + id).show();
  });
}
else
{
  $(".movie-data-section-child").before('<div class ="mobile-button-section"><div class="mobile-movie-detail">Detail</div><div class="mobile-social-detail">Social</div></div>');
  $(".part2").hide();
  $(".mobile-movie-detail").addClass("active");
  $(".mobile-movie-detail").click(function(){
    $(".mobile-movie-detail, .mobile-social-detail").removeClass("active");
    $(".mobile-movie-detail").addClass("active");
    $(".part").show();
    $(".part2").hide();
  });
  $(".mobile-social-detail").click(function(){
    $(".part").hide();
    $(".part2").show();
    $(".mobile-movie-detail, .mobile-social-detail").removeClass("active");
    $(".mobile-social-detail").addClass("active");
  });

  $(".tabs.tabs-style-bar").hide();
  $(".part4 .news-summary").hide();
  $(".music-section-data").hide();
  $(".song-head-label-5").click(function(){
    $(".music-section-data").toggle();
  });

  $(".songs-row").hide();
  $(".movie-head-label-5").click(function(){
    $(".songs-row").toggle();
  });
  $(".part7 .quote-section-one").hide();
  $(".part7 .head-label-5").click(function(){
    $(".part7 .quote-section-one").toggle();
  });
}

$(".social-part").hide();
$(".social-part1").show();
$('.social-tab').click(function() {
  $('.social-tab').removeClass('active');
  $(this).addClass('active');
  var id = $(this).attr('data'); 
  $(".social-part").hide();
  $("." + id).show();
});

$(".review-part").hide();
$(".review-part1").show();
$('.review-tab').click(function() {
  $('.review-tab').removeClass('active');
  $(this).addClass('active');
  var id = $(this).attr('data'); 
  $(".review-part").hide();
  $("." + id).show();
});

$(".change-text-div span").each(function(index) {
  $(this).delay(400*index).fadeIn(300);
});
    
// on click news pagination body scroll top
$(".pagination-reviews-box li:first a").addClass("active");
$(".pagination-news-page li:first a").addClass("active");

$('.pagination-reviews-box li a').click(function(){
  $(".pagination-reviews-box li a").removeClass("active");
  $(this).addClass("active");
  $('html, body').animate({
    scrollTop: $('.movie-data-section').offset().top - 75
  }, 500);
  return false;
});

$('.pagination-news-page li a').click(function(){
  $(".pagination-news-page li a").removeClass("active");
  $(this).addClass("active");
  $('html, body').animate({
    scrollTop: $('.movie-data-section').offset().top - 75
  }, 500);
  return false;
});

$(".helptext").hover(function(){
  $(this).toggleClass("showhelptext");
});

});

$(document).ready(function(){
  $(".lyrics-button").click(function(e) {
    e.preventDefault();
    var $div = $(this).parent().parent().parent().find('.lyrics-text');
    $(".lyrics-text").not($div).hide();
    if ($div.is(":visible")) {
      $div.hide()
    }  else {
     $div.show();
   }
 });
  $(document).click(function(e){
    var p = $(e.target).closest('.music-section-data').length
    if (!p) {
      $(".lyrics-text").hide();
    }
  });
});

function showPics(moviename) {
  $(function () {
    'use strict';
    $.ajax({
      url: '/get_pics/' + moviename,
    }).done(function (result) {
      var linksContainer = $('#SocialPics'), baseUrl;
      $.each(result.data, function (index, photo) {
        var baseUrl = photo[0];
        var img = $('<img>').prop('src', baseUrl).prop('class' , 'imgsize');
        var a = $('<a/>')
        .append(img)
        .prop('href', baseUrl)
        .prop('title', "")
        .attr('data-gallery', '')
        .appendTo(linksContainer);
      });
    });
    var borderless = true;
    $('#blueimp-gallery').data('useBootstrapModal', !borderless);
    $('#blueimp-gallery').toggleClass('blueimp-gallery-controls', borderless);
  });
}

function showIt(content, moviename, page) {
 if (content == 'image'){
  incrementImageIndex();
  page = imageIndex;
 }
 
 $.ajax({
  url: '/get/' + content + '/' + moviename + "/" + page,
  type: 'POST',
  dataType: 'html',
  data: $(this).serialize(),
  success: function(newContent){
    newContent = JSON.parse(newContent);
    $('#pagination-' + content).html("");
    $('#pagination-' + content).html(newContent.data);
  }
});
 return false;
}

function getmovienames(tag) {
  if ( tag.substring(0,5) == "Sort:" )
  {
    var tagger = $(".sort-tags1 span.active").text();
    tag = tag + "-" + tagger  
  }

  $('#moviePan').html("");
  $('.ajaxloader').show()
  $.ajax({
    url: '/getmovienames/' + tag,
    type: 'POST',
    dataType: 'html',
    data: $(this).serialize(),
    success: function(res){
      $('.ajaxloader').hide()
      res = JSON.parse(res);
      $('#moviePan').html("");
      $('#moviePan').html(res.data);
    }
  });
  return false;
}

function showTweets(moviename, label) {
  $('.ajaxloader-tweets').show()
 $.ajax({
  url: '/getTweets/' + moviename + '/15',
  type: 'POST',
  dataType: 'html',
  data: $(this).serialize(),
  success: function(newContent){
    $('.ajaxloader-tweets').hide()
    newContent = JSON.parse(newContent);
    if (label == "pos"){
      $('.pos-tweets').html(newContent.pos);
      $('.neg-tweets').html("");
      $('.pop-tweets').html("");  
      $('#pagination-reviews').html("");
    }
    else if(label == "neg"){
      $('.pos-tweets').html("");
      $('.neg-tweets').html(newContent.neg);
      $('.pop-tweets').html("");  
      $('#pagination-reviews').html("");
    }
    else if(label == "pop"){
      $('.pos-tweets').html("");
      $('.neg-tweets').html("");
      $('.pop-tweets').html(newContent.pop); 
      $('#pagination-reviews').html("");
    }
    else if(label == 'reviews'){
      $('.pos-tweets').html("");
      $('.neg-tweets').html("");
      $('.pop-tweets').html(""); 
      showIt('reviews', moviename, 1);
    }

  }
});
 return false;
}

function showUsers(moviename, limit) {
 $.ajax({
  url: '/get_users/' + moviename + '/' + limit,
  type: 'POST',
  dataType: 'html',
  data: $(this).serialize(),
  success: function(newContent){
    newContent = JSON.parse(newContent);
    imageContent = newContent.img
    infContent = newContent.inf
    $('.image-collage').html(imageContent);
    $('.influencers-ajax').html(infContent);
  }
});
 return false;
}

$(document).ready(function() {
  var display = $(".crisp-text").hide(),
  current = 0;
  display.eq(0).show();
  function showNext() {
    display.eq(current).delay(3000).fadeOut('fast', function() {
      current++;
      display.eq(current).fadeIn('fast');
      showNext();
    });
  }
  setTimeout(function() { showNext(); }, 3000);
});

$(document).ready(function() {
  $(".sort-tags span").click(function(){
    $(".sort-tags span").removeClass("active");
    $(this).addClass("active");
  });
});

$(document).ready(function() {
  $(".sort-tags1 span").click(function(){
    $(".sort-tags1 span").removeClass("active");
    $(this).addClass("active");
  });
});

$(document).ready(function() {
  $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});

$(document).ready(function() {


    $(".social-image").fancybox({
        helpers : {
        title: {
            type: 'inside',
            position: 'bottom'
        }
    },
      'zoomSpeedIn': 300,
      'zoomSpeedOut': 300,
      'overlayShow': false
    }); 







  var showChar = 200; 
  var ellipsestext = "...";
  var moretext = "more ...";
  var lesstext = "less ...";
  $('.summary_data').each(function() {
    var content = $(this).html();
    if(content.length > showChar) {
      var c = content.substr(0, showChar);
      var h = content.substr(showChar, content.length - showChar);
      var html = c + '<span class="moreellipses">' + ellipsestext+ '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';
      $(this).html(html);
    }
  });

$(".morelink").click(function(){
  if($(this).hasClass("less")) {
    $(this).removeClass("less");
    $(this).html(moretext);
  } else {
    $(this).addClass("less");
    $(this).html(lesstext);
  }
  $(this).parent().prev().toggle();
  $(this).prev().toggle();
  return false;
});
});
$(this).parent().prev().toggle(100);
$(this).prev().toggle(100);

$(window).load(function() {
  $(".fbajax").html('<div id="fb-root"></div><script>(function(d, s, id) {var js, fjs = d.getElementsByTagName(s)[0];if (d.getElementById(id)) return;js = d.createElement(s); js.id = id;js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.4&appId=1526470804243594";fjs.parentNode.insertBefore(js, fjs);}(document, "script", "facebook-jssdk"));</script><div class="fb-page" data-href="https://www.facebook.com/sociofuzz" data-width="300"data-height="300" data-small-header="false" data-adapt-container-width="true" data-hide-cover="false" data-show-facepile="false" data-show-posts="true"><div class="fb-xfbml-parse-ignore"><blockquote cite="https://www.facebook.com/sociofuzz"><a href="https://www.facebook.com/sociofuzz">SocioFuzz</a></blockquote></div></div>');
  $(".fblike").html('<div class="fb-page" data-href="https://www.facebook.com/sociofuzz" data-width="300" data-hide-cover="false" data-show-facepile="false" data-show-posts="false"></div>')
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

var imageIndex = 1;
function incrementImageIndex() 
{
  imageIndex++;
}





