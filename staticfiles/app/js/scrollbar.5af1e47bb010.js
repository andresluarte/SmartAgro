TB.render('component_ID',function(data){
    data.ele.find('.top-scroll-wrapper').remove();
    var customScrollBar = $('<div class="top-scroll-wrapper"><div class="top-scroll"></div></div>');
    data.ele.prepend(customScrollBar);
    
    var getAndSetWidth = function(){
        var wrapperWidth = data.ele.find(' .table-responsive').width() +'px';
        var scrollWidth =  data.ele.find(' table').width() +'px';
        console.log(wrapperWidth,scrollWidth);
        data.ele.find(' .top-scroll-wrapper').css('width',wrapperWidth);
        data.ele.find(' .top-scroll').css('width',scrollWidth);
    };
    getAndSetWidth();
    $(window).on('resize', function(){
        getAndSetWidth();
    });
    data.ele.find(' .top-scroll-wrapper').scroll(function(){
        data.ele.find(' .table-responsive')
            .scrollLeft(data.ele.find(' .top-scroll-wrapper').scrollLeft());
    });
    data.ele.find(' .table-responsive').scroll(function(){
        data.ele.find(' .top-scroll-wrapper')
            .scrollLeft(data.ele.find(' .table-responsive').scrollLeft());
    });
});