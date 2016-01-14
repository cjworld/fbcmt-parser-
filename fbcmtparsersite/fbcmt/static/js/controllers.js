/* global angular */

var fbcmtControllers = angular.module('fbcmtControllers', []);

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
