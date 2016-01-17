/* global angular */

var fbcmtControllers = angular.module('fbcmtControllers', []);


fbcmtControllers.controller('FbPostCtlr', ['$scope', '$http', function ($scope, $http) {
    $scope.loader = {
      loading: false,
    };
    $scope.google_mail = null;
    $scope.reply_on_post = false;
    $scope.facebook_url = null;
    
    $scope.total_value = 0;
    $scope.message_array = {};
    /*{
        "+1": {
            code: "default",
            value: 0,
            text: "+1sassssssssssss",
            comments: []
        }
    }*/
    
    $scope.sumup = function() {
        $scope.total_value = 0;
        angular.forEach($scope.message_array, function(message, key) {
            var value = message.value;
            var amount = message.comments.length;
            $scope.total_value += value * amount;
        });
    }
    
    $scope.plus = function(message) {
        message.value += 1;
        $scope.sumup();
    }
    $scope.minus = function(message) {
        message.value -= 1;
        $scope.sumup();
    }
    
    $scope.get_messages = function(){
      $scope.message_array = {};
      $scope.loader.loading=true;
      $http({
        method: 'GET',
        url: 'fbghapi/comments',
        params: {
            facebook_url: $scope.facebook_url,
            reply_on_post: $scope.reply_on_post
        }
      }).then(function(result) {
        $scope.loader.loading=false;
        console.log(result);
        if (result.status == 200) {
            angular.forEach(result.data.data, function(value, key) {
                var message = value.message;
                if(!$scope.message_array.hasOwnProperty(message)) {
                    $scope.message_array[message] = {
                        code: "default",
                        value: 0,
                        text: message,
                        comments: []
                    }
                }
                $scope.message_array[message]['comments'].push(value);
            });
        }
      }, function(errorMsg) {
        $scope.loader.loading=false;
      });
    };
    
    $scope.convert = function(){
        var spreadsheet_data = {
        };
      
        angular.forEach($scope.message_array, function(message, key) {
            var value = message.value;
            angular.forEach(message.comments, function(comment, key) {
                var user_id = comment.from.id;
                if(!spreadsheet_data.hasOwnProperty(user_id)) {
                    spreadsheet_data[user_id] = {
                        'name': comment.from.name,
                        'value': value
                    }
                }
                else {
                    spreadsheet_data[user_id]['value'] += value;
                }
            });
        });
        
        console.log(spreadsheet_data);
        
        $scope.loader.loading=true;
        $http({
            method: 'GET',
            url: 'ggdrvapi/ss/new',
            params: {
                google_mail: $scope.google_mail,
                spreadsheet_data: spreadsheet_data
            }
        }).then(function(result) {
            $scope.loader.loading=false;
        }, function(errorMsg) {
            $scope.loader.loading=false;
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
