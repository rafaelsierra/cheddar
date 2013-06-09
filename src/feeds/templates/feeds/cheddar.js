/*
 * This script, yet seems like a jQuery plugin, is pretty much linked with
 * every HTML tag in the site, I just did for the sake of organization 
 */
(function($) {

    var urls = {
        'STATIC_URL': '{{STATIC_URL|escapejs}}',
        'MEDIA_URL': '{{MEDIA_URL|escapejs}}',
        'mysites': "{% url 'feeds:my-sites' %}",
        'post_list_read': "{% url 'feeds:post-list-read' %}",
        'post_list_unread': "{% url 'feeds:post-list-unread' %}",
        'post_list_starred': "{% url 'feeds:post-list-starred' %}",
        'mark_post_as_read': "{% url 'feeds:post-mark-as-read' %}",
        'mark_all_posts_as_read': "{% url 'feeds:post-mark-all-as-read' %}",
        'star_post': function(postId){return "{% url 'feeds:post-star-it' pk='POSTID' %}".replace('POSTID', postId);}
    };
    
    var post_list_state = {
        reset: function(){
            this.is_read = false;
            this.is_starred = false;
            this.page = 1;
            this.site = null;
            this.folder = null;
        }
    };
    
    var sitelist_ovescroll_config = {direction:'vertical', hoverThumbs: true}
    
    var navigation_state = {current_post:null};


    function update_container_height(){
        var height = window.innerHeight - $("#top-bar").height();
        $("#postlist, #left-bar").height(height);
    }

    function mark_all_as_read(){
        $("#markAllAsReadModal .spin").show();
        $("#markAllAsReadModal button").hide();
        $.ajax({
            type:'POST',
            url: urls.mark_all_posts_as_read,
            success: function(response){
                $("#markAllAsReadModal .spin").fadeOut();
                $("#markAllAsReadModal button").fadeIn();
                $("#markAllAsReadModal p:not(.alert)").hide();
                $("#markAllAsReadModal p.alert").show();
            }
        })
    }    

    function read_post(article){
        // TODO: Collapsable posts
        
        // Open and mark post as read
        $("#postlist .active").removeClass("active");
        article.addClass("active");
        var post_content = article.find('.post-content');
        var site = $("#site-"+article.data('site_id'));
        var counter = site.find('.unread-counter');

        if(!article.hasClass('post-read')){
            counter.text(counter.text()-1);
            $.cheddar('markAsRead', article.data("post_id"));
        }
        
        window.location.hash = 'post-'+article.data('post_id');
        window.scrollBy(0, -55);
        
        var unread_posts = $("#postlist article:not(.post-read)");
        if(unread_posts.length == 0){
            post_list_state.page++;
            $.cheddar('loadPosts');
        }
        
    }
    
    function star_post(article){
        var postId = article.data("post_id");
        $.ajax({
            url:urls.star_post(postId),
            type:'POST',
            success: function(response){
                article.find('.star-post i').toggleClass('icon-star').toggleClass('icon-star-empty');
            },
            dataType:'json'
        });
    }
    
    function move_cursor_to(next_or_previous){
            var current_post;  
            if(!navigation_state.current_post){
                navigation_state.current_post = $("#postlist article.post").first();
            }else{
                if(next_or_previous == 'next'){
                    var next = navigation_state.current_post.next();
                    if(next.length>0){
                        navigation_state.current_post = next;
                    }
                }else{
                    var previous = navigation_state.current_post.prev();
                    if(previous.length>0){
                        navigation_state.current_post = previous;
                    }
                    
                }
            }
            navigation_state.current_post.find('header').click();            
    }
    
    function move_cursor_to_next(){
        move_cursor_to('next');
    }
    
    function move_cursor_to_previous(){
        move_cursor_to('previous');
    }
    
    function clear_posts(){
        $("#postlist").html('');
    }
        
    var methods = {
        init: function(options){
            // Configure "Loading"
            var ajaxStackCount = 0;
            $(document).ajaxStart(function(){
                $(".loading").show();
            });
            $(document).ajaxStop(function(){
                $(".loading").hide();
            });
            
            // One Ring to bring them all and in the darkness bind them
            post_list_state.reset();

            // Reading posts event
            $("#postlist").on('click', 'article.post header', function(){
                read_post($(this).parent());
            });
            
            $("#postlist").on('click', '.star-post', function(){
                var tag = $(this).parent();
                // Travese DOM tree backwards to find where is the article
                while(tag.prop('tagName')!='ARTICLE'){
                    tag = tag.parent();
                }
                star_post(tag)
            });
            
            $("#starred-button").on('click', function(){
                post_list_state.reset();
                post_list_state.is_starred = true;   
                clear_posts();
                $.cheddar('loadPosts');   
            })
            
            $("#sites-container").on('click', '.site-button', function(){
                // Loads posts only from this site
                clear_posts();
                post_list_state.folder = null;
                post_list_state.page = 1;
                post_list_state.site = $(this).data('site');
                $.cheddar('loadPosts');
            })
            
            
            $("#sites-container").on('click', '.site-folder a', function(){
                // Loads posts only from this folder
                clear_posts();
                post_list_state.folder = $(this).data('folder');
                post_list_state.page = 1;
                post_list_state.site = null;
                $.cheddar('loadPosts');
            })
            
            
            $("#sites-container").on('click', '.site-folder i', function(){
                $(this).toggleClass('icon-folder-open').toggleClass('icon-folder-close')
                $(this).parent().parent().find('ul').slideToggle();
            });
            
            $("#refresh-button").click(function(){$.cheddar("refresh");})
            
            $("#doMarkAllAsRead").click(function(){mark_all_as_read();})
            
            // Binds hotkeys
            $(document).bind('keypress', 'j', move_cursor_to_next);
            $(document).bind('keypress', 'k', move_cursor_to_previous);
            $(document).bind('keypress', 's', function(){
                if(navigation_state.current_post){
                    star_post(navigation_state.current_post);
                }
            });
            $(document).bind('keypress', 'r', function(){
                $.cheddar('refresh');
            });
            
            // Container height
            update_container_height();
            $(window).resize(update_container_height);
            return this;
        },
        
        loadSites: function(){
            $.ajax({
                url: urls.mysites,
                dataType: 'html',
                success: function(response){
                    // Clear the current list of sites
                    $("#feed-list").siblings().remove();
                    // Loads the new one
                    $("#feed-list").parent().append(response);
                    $.cheddar('updateFolders');
                }
            });
            return this;
        },
        
        updateFolders: function(){
            var folders = {}; // List of folders
            var sites = $("#sites-container li");
            
            // Load folders
            $.each(sites, function(i, site){   
                site = $(site);         
                if(!site.data('folder')){ return; }
                
                var id = site.data('folder_id');
                folders[id] = site.data('folder');
            });
            
            // Create folders into list
            $.each(folders, function(id, folder){
                var li = '<li id="folder-'+id+'" class="site-folder"><a href="javascript:void(0);" data-folder="'+id+'"><i class="icon-folder-close folder-button"></i> '+folder+'</a><ul class="nav nav-list"></ul></li>';
                $(li).insertAfter("#feed-list");
                $("#sites-container li[data-folder_id="+id+"]").detach().appendTo("#folder-"+id+' ul');
                $("#folder-"+id+" ul").hide();
            });
            
        },
        
        loadPosts: function(){
            var data = {};
            var url = post_list_state.is_read?urls.post_list_read:urls.post_list_unread;
            
            data['page'] = post_list_state.page;
            
            if(post_list_state.site){
                data['site'] = post_list_state.site;
            }else if(post_list_state.folder){
                data['folder'] = post_list_state.folder; 
            }
            
            if(post_list_state.is_starred){
                url = urls.post_list_starred;
            }

            $.ajax({
                'url': url,
                'data': data, // That's why I hate this with javascript
                success: function(response){
                    $("#postlist").append(response);
                    // Change all <a> to target=_blank
                    $("#postlist .post-content a").attr('target', '_blank');
                },
                dataType: 'html'
                
            });
            return this;
        },
        
        markAsRead: function(post_id){
            // Mark this post as read
            $.post(urls.mark_post_as_read, {id:post_id} ,function(response){
                $("#post-"+post_id).addClass('post-read');
            }, 'json');
        },
        
        refresh: function(){
            $("#feed-list").siblings().remove();
            $("#postlist").html('');
            $.cheddar('loadSites').cheddar('loadPosts');
            navigation_state.current_post = null;
        }
    };

    $.cheddar = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.cheddar');
        }
    };

})(jQuery); 