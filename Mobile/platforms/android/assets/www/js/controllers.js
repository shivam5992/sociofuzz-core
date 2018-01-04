'use strict';

angular.module('starter.controllers', ['easypiechart'])
.controller('AppCtrl', function($scope, $ionicModal, $ionicPopover, $timeout) {
    $scope.loginData = {};
    $scope.isExpanded = false;
    $scope.hasHeaderFabLeft = false;
    $scope.hasHeaderFabRight = false;
    var navIcons = document.getElementsByClassName('ion-navicon');
    for (var i = 0; i < navIcons.length; i++) {
        navIcons.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
    $scope.hideNavBar = function() {
        document.getElementsByTagName('ion-nav-bar')[0].style.display = 'none';
    };

    $scope.showNavBar = function() {
        document.getElementsByTagName('ion-nav-bar')[0].style.display = 'block';
    };

    $scope.noHeader = function() {
        var content = document.getElementsByTagName('ion-content');
        for (var i = 0; i < content.length; i++) {
            if (content[i].classList.contains('has-header')) {
                content[i].classList.toggle('has-header');
            }
        }
    };

    $scope.setExpanded = function(bool) {
        $scope.isExpanded = bool;
    };

    $scope.setHeaderFab = function(location) {
        var hasHeaderFabLeft = false;
        var hasHeaderFabRight = false;

        switch (location) {
            case 'left':
            hasHeaderFabLeft = true;
            break;
            case 'right':
            hasHeaderFabRight = true;
            break;
        }
        $scope.hasHeaderFabLeft = hasHeaderFabLeft;
        $scope.hasHeaderFabRight = hasHeaderFabRight;
    };

    $scope.hasHeader = function() {
        var content = document.getElementsByTagName('ion-content');
        for (var i = 0; i < content.length; i++) {
            if (!content[i].classList.contains('has-header')) {
                content[i].classList.toggle('has-header');
            }
        }

    };

    $scope.hideHeader = function() {
        $scope.hideNavBar();
        $scope.noHeader();
    };

    $scope.showHeader = function() {
        $scope.showNavBar();
        $scope.hasHeader();
    };

    $scope.clearFabs = function() {
        var fabs = document.getElementsByClassName('button-fab');
        if (fabs.length && fabs.length > 1) {
            fabs[0].remove();
        }
    };
})

.controller('HomeCtrl', function($scope, $timeout, $stateParams, ionicMaterialInk, $http) {
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $timeout(function() {
        $scope.isExpanded = false;
        $scope.$parent.setExpanded(false);
    }, 100);
    $http.get('http://www.sociofuzz.com/appindex').then(function(resp) {
        $scope.index1 = resp.data;
    }, function(err) {
        console.error('ERR', err);
    })


})

.controller('AboutusCtrl', function($scope, $stateParams, $timeout, ionicMaterialInk, ionicMaterialMotion, $http) {
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.$parent.setHeaderFab('left');
    $timeout(function() {
        $scope.isExpanded = false;
        $scope.$parent.setExpanded(false);
    }, 300);
    ionicMaterialMotion.fadeSlideInRight();
    ionicMaterialInk.displayEffect();
})

.controller('TriviasCtrl', function($scope, $stateParams, $timeout, ionicMaterialInk, ionicMaterialMotion, $http) {
    var mname = $stateParams.moviename;
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.$parent.setHeaderFab('left');
    $timeout(function() {
        $scope.isExpanded = false;
        $scope.$parent.setExpanded(false);
    }, 300);
    ionicMaterialMotion.fadeSlideInRight();
    ionicMaterialInk.displayEffect();
    $http.get('http://www.sociofuzz.com/app/trivias/' + mname).then(function(resp) {
        $scope.trivias = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
})



.controller('ProfileCtrl', function($scope, $stateParams, $timeout, ionicMaterialMotion, ionicMaterialInk, $http) {
    var mname = $stateParams.moviename;
    $scope.uname = mname;
    $http.get('http://www.sociofuzz.com/app/movie/' + mname).then(function(resp) {
        $scope.movie_data = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
    $http.get('http://www.sociofuzz.com/getTweets/' + mname + '/10').then(function(resp) {
        $scope.tweets = {};
        $scope.tweets.pos = resp.data.pos;
        $scope.tweets.neg = resp.data.neg;
        $scope.tweets.pop = resp.data.pop;
        $scope.CurrentTwit = $scope.tweets.pop;$scope.tweets.pop;
        $scope.showTwit = function(flag)
        {   
            if (flag == 'p'){
                $scope.CurrentTwit = $scope.tweets.pos;
            }
            else if (flag == 'n'){
                $scope.CurrentTwit = $scope.tweets.neg;
            }
            else
            {
                $scope.CurrentTwit = $scope.tweets.pop;
            }
        }

    }, function(err) {
        console.error('ERR', err);
    })
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab(false);
    $timeout(function() {
        ionicMaterialMotion.slideUp({
            selector: '.slide-up'
        });
    }, 300);
    $timeout(function() {
        ionicMaterialMotion.fadeSlideInRight({
            startVelocity: 3000
        });
    }, 700);
    ionicMaterialInk.displayEffect();
})




.controller('NewsCtrl', function($scope, $stateParams, $timeout, ionicMaterialMotion, ionicMaterialInk, $http) {
    var mname = $stateParams.moviename;
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab('right');
    $timeout(function() {
        ionicMaterialMotion.fadeSlideIn({
            selector: '.animate-fade-slide-in .item'
        });
    }, 200);
    ionicMaterialInk.displayEffect();
    $http.get('http://www.sociofuzz.com/appcontent/news/' + mname).then(function(resp) {
        $scope.news = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
    $scope.itemDetail = function(link){
        window.open(link, '_blank');   
    };
})


.controller('AllMoviesCtrl', function($scope, $stateParams, $timeout, ionicMaterialMotion, ionicMaterialInk, $http) {
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab('right');
    $timeout(function() {
        ionicMaterialMotion.fadeSlideIn({
            selector: '.animate-fade-slide-in .item'
        });
    }, 200);
    ionicMaterialInk.displayEffect();
    $http.get('http://sociofuzz.com/getAllMovies').then(function(resp) {
        $scope.moviesall = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
})


.controller('AboutCtrl', function($scope, $stateParams, $timeout, ionicMaterialMotion, ionicMaterialInk, $http, $sce) {
    
    $scope.trustSrc = function(src) {
    return $sce.trustAsResourceUrl(src);
    }

    var mname = $stateParams.moviename;
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab('right');
    $timeout(function() {
        ionicMaterialMotion.fadeSlideIn({
            selector: '.animate-fade-slide-in .item'
        });
    }, 200);
    // ionicMaterialInk.displayEffect();
    $http.get('http://www.sociofuzz.com/app/about/' + mname).then(function(resp) {
        $scope.about = resp.data.data;
        $scope.about.trailer = "https://www.youtube.com/embed/" + $scope.about.trailerId + "?rel=0&modestbranding=1&autohide=1&showinfo=0&controls=0";
    }, function(err) {
        console.error('ERR', err);
    })
})




.controller('CriticsCtrl', function($scope, $stateParams, $timeout, ionicMaterialMotion, ionicMaterialInk, $http) {
    var mname = $stateParams.moviename;
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab('right');
    $http.get('http://www.sociofuzz.com/appcontent/reviews/' + mname).then(function(resp) {
        $scope.review_data = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
    $timeout(function() {
        ionicMaterialMotion.fadeSlideIn({
            selector: '.animate-fade-slide-in .item'
        });
    }, 200);
    ionicMaterialInk.displayEffect();
    $scope.itemDetail = function(link){
        window.open(link, '_blank'); 
    };
})





.controller('SocialCtrl', function($scope, $stateParams, $timeout, ionicMaterialInk, ionicMaterialMotion, $http) {
    var mname = $stateParams.moviename;
    $scope.$parent.showHeader();
    $scope.$parent.clearFabs();
    $scope.isExpanded = false;
    $scope.$parent.setExpanded(false);
    $scope.$parent.setHeaderFab(false);
    ionicMaterialInk.displayEffect();
    ionicMaterialMotion.pushDown({
        selector: '.push-down'
    });
    ionicMaterialMotion.fadeSlideInRight({
        selector: '.animate-fade-slide-in .item'
    });
    $http.get('http://www.sociofuzz.com/app/analyzed/' + mname).then(function(resp) {
    $scope.anal = resp.data.data;
    }, function(err) {
        console.error('ERR', err);
    })
})





.controller('chartCtrlP', ['$scope', function ($scope) {
    $scope.percent = 23;
    $scope.options = {
        animate:{
            duration:0,
            enabled:false
        },
        barColor:'green',
        scaleColor:false,
        lineWidth:6,
        lineCap:'circle'
    };
}])
.controller('chartCtrlN', ['$scope', function ($scope) {
    $scope.percent = 15;
    $scope.options = {
        animate:{
            duration:0,
            enabled:false
        },
        barColor:'#ED133B',
        scaleColor:false,
        lineWidth:6,
        lineCap:'circle'
    };
}])
.controller('chartCtrlNU', ['$scope', function ($scope) {
    $scope.percent = 5;
    $scope.options = {
        animate:{
            duration:0,
            enabled:false
        },
        barColor:'#35B9E6',
        scaleColor:false,
        lineWidth:6,
        lineCap:'circle'
    };
}]);