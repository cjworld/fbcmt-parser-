import requests
import json


DEBUG = False


def get_object_id(url):
    """
    Get object id from url
    """
    tokens = url.split("/")
    if "m.facebook.com" in tokens:
        tokens2 = tokens[-1].split("?")[-1].split("&")
        for tok2 in tokens2:
            if tok2.startswith("id="):
                return tok2.split("=")[-1]
    else:
        object_id = tokens[-2]
        return object_id
    return None
    
    
def get_graph_api_url(object_id, access_token, edge_name=None):
    """
    Get url of graph api for object id
    """
    if edge_name is None:
        return 'https://graph.facebook.com/v2.2/%s?access_token=%s&format=json&method=get&pretty=0' % (object_id, access_token)
    else:
        return 'https://graph.facebook.com/v2.2/%s/%s?access_token=%s&format=json&method=get&pretty=0' % (object_id, edge_name, access_token)


def get_graph_api_query(object_id, access_token, edge_name=None, graph_api_url=None):
    if graph_api_url is None:
        graph_api_url = get_graph_api_url(object_id, access_token, edge_name)
    if DEBUG:
        print 'graph_api_url:', graph_api_url
    res = requests.get(graph_api_url)
    json_dict = json.loads(res.text)
    if DEBUG:
        print 'res.text:', res.text
        print 'json_dict:', json_dict
    return json_dict
    
    
def get_comments(object_id, access_token):
    ttl_ret = {'data':[]}
    ret = get_graph_api_query(object_id, access_token, edge_name="comments")
    if DEBUG:
        print 'get_graph_api_query:', ret
    if ret.get('error') is not None:
        return ret
    ttl_ret['data'] = ret.get('data')
    if DEBUG:
        print 'next_graph_api_url:', ret.get('paging')
    while ret.get('paging') is not None and ret.get('paging').get('next') is not None:
        next_graph_api_url = ret.get('paging').get('next')
        if DEBUG:
            print 'next_graph_api_url:', ret.get('paging').get('next')
        ret = get_graph_api_query(object_id, access_token, edge_name="comments", graph_api_url=next_graph_api_url)
        if ret.get('error') is not None:
            return ret
        ttl_ret['data'] = ttl_ret['data'] + ret.get('data')
    return ttl_ret
    
    
def parse_comment_result(json_dict):
    users_dict = {}
    comments_list = []
    for comment in json_dict['data']:
        user_info = comment['from']
        user_id = user_info['id']
        if user_id not in users_dict.keys():
            users_dict[user_id] = user_info
        if DEBUG:
            print 'comment:', comment
        comments_list.append(comment)
    return users_dict, comments_list

    
def customized_parser(url, access_token, reply_on_post=False):
    total_comments_dict = []
    
    object_id = get_object_id(url)
    if DEBUG:
        print 'object_id:', object_id
    if object_id is None:
        return {"error": "undefined object"}
    
    ret = get_graph_api_query(object_id, access_token)
    if ret.get('error') is not None:
        return ret
    author_id = ret.get('from').get('id')
    author_username = ret.get('from').get('name')
    author_message = ret.get('message')
    if DEBUG:
        print 'author_id:', author_id
        print 'author_username:', author_username
        print 'author_message:', author_message
    
    ret = get_comments(object_id, access_token)
    users_dict, comments_list = parse_comment_result(ret)
    if DEBUG:
        print 'users_dict:', users_dict
        print 'comments_list:', comments_list
    if reply_on_post is True:
        total_comments_dict.append({
            'username': author_username,
            'message': author_message,
            'comments': comments_list,
            'comment_level': 2
        })
    
    for comment_idx, comment in enumerate(comments_list):
        if comment['from']['id'] == author_id or reply_on_post is True:
            object_id = comment['id']
            if DEBUG:
                print 'object_id:', object_id
            ret = get_comments(object_id, access_token)
            users_dict_lv2, comments_list_lv2 = parse_comment_result(ret)
            users_dict.update(users_dict_lv2)
            if reply_on_post is True:
                total_comments_dict[0]['comments'][comment_idx] = [total_comments_dict[0]['comments'][comment_idx]] + comments_list_lv2
            else:
                total_comments_dict.append({
                    'username': comment['from']['name'],
                    'message': comment['message'],
                    'comments': comments_list_lv2,
                    'comment_level': 1
                })
    if DEBUG:
        print 'users_dict:', users_dict
        print 'total_comments_dict:', total_comments_dict
    
    return {'users':users_dict, 'posts':total_comments_dict}
    