var fbcmtServices = angular.module('fbcmtServices', ['ngResource']);

fbcmtServices.factory('User', ['$resource', function($resource){
    return $resource('users/:id', {}, {
        query: {method:'GET', params:{username:'@id'}, isArray:true}
    });
}]);

fbcmtServices.factory('Post', ['$resource', function($resource){
    return $resource('posts/:id', {id:'@id'}, {
        query: {method:'GET', params:{id:'@id'}, isArray:true}
    }, {stripTrailingSlashes: false});
}]);

fbcmtServices.factory('Photo', ['$resource', function($resource){
    return $resource('photos/:id', {}, {
        query: {method:'GET', params:{id:'@id'}, isArray:true}
    });
}]);

fbcmtServices.factory('UserPost', ['$resource', function($resource){
    return $resource('users/:username/posts', {}, {
        query: {method:'GET', params:{username:'@username'}, isArray:true}
    });
}]);

fbcmtServices.factory('PostPhoto', ['$resource', function($resource){
    return $resource('posts/:post_id/photos', {}, {
        query: {method:'GET', params:{post_id:'@post_id'}, isArray:true}
    });
}]);
