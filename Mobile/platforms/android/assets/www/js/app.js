angular.module('starter', ['ionic', 'starter.controllers', 'ionic-material', 'ionMdInput'])

.run(function($ionicPlatform) {
    $ionicPlatform.ready(function() {
        if (window.cordova && window.cordova.plugins.Keyboard) {
            cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
        }
        if (window.StatusBar) {
            StatusBar.styleDefault();
        }
    });
})

.config(function($stateProvider, $urlRouterProvider, $ionicConfigProvider) {
    $ionicConfigProvider.views.maxCache(0);
    $stateProvider.state('app', {
        url: '/app',
        abstract: true,
        templateUrl: 'templates/menu.html',
        controller: 'AppCtrl'
    })

.state('app.critics', {
    url: '/critics/:moviename',
    views: {
        'menuContent': {
            templateUrl: 'templates/critics.html',
            controller: 'CriticsCtrl'
        },
        
    }
})

.state('app.aboutus', {
        url: '/aboutus',
        views: {
            'menuContent': {
                templateUrl: 'templates/aboutus.html',
                controller: 'AboutusCtrl'
            }
        }
    })

.state('app.about', {
        url: '/about/:moviename',
        views: {
            'menuContent': {
                templateUrl: 'templates/about.html',
                controller: 'AboutCtrl'
            }
        }
    })


.state('app.music', {
        url: '/music/:moviename',
        views: {
            'menuContent': {
                templateUrl: 'templates/music.html',
                controller: 'MusicCtrl'
            },
            'fabContent': {
                template: '<button id="fab-music" class="button button-fab button-fab-top-right expanded button-energized-900 flap"><i class="icon ion-paper-airplane"></i></button>',
                controller: function ($timeout) {
                    $timeout(function () {
                        document.getElementById('fab-music').classList.toggle('on');
                    }, 200);
                }
            }
        }
    })


.state('app.news', {
        url: '/news/:moviename',
        views: {
            'menuContent': {
                templateUrl: 'templates/news.html',
                controller: 'NewsCtrl'
            },
            
        }
    })

.state('app.trivias', {
    url: '/trivias/:moviename',
    views: {
        'menuContent': {
            templateUrl: 'templates/trivias.html',
            controller: 'TriviasCtrl'
        },
        
    }
})

.state('app.social', {
    url: '/social/:moviename',
    views: {
        'menuContent': {
            templateUrl: 'templates/social.html',
            controller: 'SocialCtrl'
        },
        
    }
})

.state('app.home', {
    url: '/home',
    views: {
        'menuContent': {
            templateUrl: 'templates/home.html',
            controller: 'HomeCtrl'
        }
    }
})

.state('app.profile', {
    url: '/profile/:moviename',
    views: {
        'menuContent': {
            templateUrl: 'templates/profile.html',
            controller: 'ProfileCtrl'
        }
        
    }
})

.state('app.allmovies', {
    url: '/allmovies',
    views: {
        'menuContent': {
            templateUrl: 'templates/allmovies.html',
            controller: 'AllMoviesCtrl'
        }
        
    }
});

$urlRouterProvider.otherwise('/app/home');
});
