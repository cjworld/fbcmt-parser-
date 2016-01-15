/* global angular */

var fbcmtControllers = angular.module('fbcmtControllers', []);


fbcmtControllers.controller('FbPostCtlr', ['$scope', '$http', function ($scope, $http) {
    $scope.loader = {
      loading: false,
    };
    $scope.google_mail = null;
    $scope.reply_on_post = false;
    $scope.facebook_url = null;
    $scope.author_posts = [];
    $scope.convert = function(){
      $scope.author_posts = [];
      $scope.loader.loading=true;
      $http({
        method: 'GET',
        url: 'fbghapi',
        params: {
            facebook_url: $scope.facebook_url,
            google_mail: $scope.google_mail,
            reply_on_post: $scope.reply_on_post
        }
      }).then(function(result) {
        $scope.loader.loading=false;
        console.log(result.data.posts);
        angular.forEach(result.data.posts, function(value, key) {
            //console.log(value);
            if (value.comment_level == 1) {
                value['comments'] = [value['comments']];
            }
            $scope.author_posts.push(value);
        });
      }, function(errorMsg) {
        $scope.loader.loading=false;
        //console.log(errorMsg);
      });
    };
}]);


fbcmtControllers.controller('PostController', ['$scope', '$q', 'Post', 'PostPhoto', function ($scope, $q, Post, PostPhoto) {
    $scope.photos = {}
    $scope.posts = Post.query();
    $scope.posts.$promise.then(function(result) {
        //console.log(result);
        angular.forEach(result, function(post, key) {
            console.log(post);
            $scope.photos[post.id] = PostPhoto.query({post_id: post.id});
            
        });
        console.log($scope.photos);
    }, function(errorMsg) {
        
    });
    
}]);


fbcmtControllers.controller('EditController', ['$scope', '$q', 'Post', function ($scope, $q, Post) {
    $scope.newPost = new Post();
    $scope.save = function(){
        $scope.newPost.$save().then(function(result) {
            $scope.posts.push(result);
            $scope.newPost = new Post();
            $scope.errors = null;
        }, function(errorMsg) {
            $scope.errors = errorMsg.data;
        });
    };
}]);


fbcmtControllers.controller('DeleteController', ['$scope', 'AuthUser', function ($scope, AuthUser) {
    $scope.canDelete = function(post){
        return post.author.username == AuthUser.username;
    };
    $scope.delete = function(post) {
        post.$delete().then(function(){
            var idx = $scope.posts.indexOf(post);
            $scope.posts.splice(idx, 1)
        }, function(errorMsg) {
            $scope.errors = errorMsg.data;
        });
        
    }
}]);
