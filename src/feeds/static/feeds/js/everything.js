(function(window, document, $, urls){
    
    function update_folder(){
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

    /**
     * Moves to the next or first post, or highlights the next button
     */
    function move_cursor_to_next(){
        // Checks if there is a post active
        var article = $("article.active");
        var next;
        if(article.length > 0){
            next = article.next('article');
            if(next.length==0){
                $("article.active").removeClass("active");
                $(document).scrollTop($("a.next").offset().top)
                $("a.next").addClass("glow").focus();
            }else{
                next.click();
                $("a.next").removeClass("glow");
            }
        }else{
            if($("a.next.glow").length > 0){
                $("a.next.glow").click();
            }else{
                $("#postlist article").first().click();
            }
        }
    }
    
    function move_cursor_to_previous(){
        // TODO: Previous button
        var article = $("article.active");
        var prev;
        if(article.length == 0){
            if($("a.next.glow").length > 0){
                prev = $("#postlist article").last();
            }else{
                return;
            }
        }else{
            prev = article.prev('article');
        }
        prev.addClass("active");
        prev.click();
        $("a.next").removeClass("glow");
    }

    /**
     * Mark the post as read and highlight it
     */
    function read_post(){
        var article = $this = $(this);
        $("article.active").removeClass('active');
        $this.addClass('active');
        
        $(document).scrollTop($this.offset().top-10);
        
        var site = $("#site-"+article.data('site_id'));
        var counter = site.find('.unread-counter');
        var post_id = article.data("post_id");
        
        if(!article.hasClass('post-read')){
            counter.text(counter.text()-1);
            $.post(urls.mark_post_as_read, {id:post_id} ,function(response){
                $("#post-"+post_id).addClass('post-read');
            }, 'json');
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

    $(document).ready(function() {
        update_folder();
        $("article.post").click(read_post);
        $(document).bind('keypress', 'j', move_cursor_to_next);
        $(document).bind('keypress', 'k', move_cursor_to_previous);
        $(document).bind('keypress', 'r', function(){window.location.reload()});
        $(document).bind('keypress', 's', function(){
            var article = $("#postlist article.active");
            if(article.length>0){
                star_post(article);
            }
        });
        
        $("#postlist").on('click', '.star-post', function(){
            var tag = $(this).parent();
            // Travese DOM tree backwards to find where is the article
            while(tag.prop('tagName')!='ARTICLE'){
                tag = tag.parent();
            }
            star_post(tag)
        });
        $("#sites-container").on('click', '.site-folder i', function(){
            $(this).toggleClass('icon-folder-open').toggleClass('icon-folder-close')
            $(this).parent().parent().find('ul').slideToggle();
        });
        $("#doMarkAllAsRead").click(function(){mark_all_as_read();})
    }); 
    
    
})(window, document, jQuery, urls);

