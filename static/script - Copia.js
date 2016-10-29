$(function(){
    var searchField = $('#query');
    var icon = $('#search-btn');

    $('#search-form').submit(function(e){
        e.preventDefault();
    });



})

function search() {
    $('#results').html('');

    q = $('#query').val();

    $.get(
        "https://www.googleapis.com/youtube/v3/search", {
            part: 'snippet, id',
            q: q,
            maxResults: 10,
            type: 'video',
            key: 'AIzaSyAyCS7wxWvJB3sG5Qmd2MOpB9J50v-NLaY'
        },
        function(data) {
            for (var i = 0; i < data.items.length; i++) {
                $.get(
                    "https://www.googleapis.com/youtube/v3/videos", {
                        part: 'snippet, contentDetails',
                        key: "AIzaSyAyCS7wxWvJB3sG5Qmd2MOpB9J50v-NLaY",
                        id: data.items[i].id.videoId
                    },
                    function(video) {
                        if (video.items.length > 0) {
                            item = video.items[0];
                            var output = getOutput(video.items[0]);
                            $('#results').append(output);

                        }
                    });
            }

        });

}


function convertTime(duration) {
    var a = duration.match(/\d+/g);

    if (duration.indexOf('M') >= 0 && duration.indexOf('H') == -1 && duration.indexOf('S') == -1) {
        a = [0, a[0], 0];
    }

    if (duration.indexOf('H') >= 0 && duration.indexOf('M') == -1) {
        a = [a[0], 0, a[1]];
    }
    if (duration.indexOf('H') >= 0 && duration.indexOf('M') == -1 && duration.indexOf('S') == -1) {
        a = [a[0], 0, 0];
    }

    duration = 0;

    if (a.length == 3) {
        duration = duration + parseInt(a[0]) * 3600;
        duration = duration + parseInt(a[1]) * 60;
        duration = duration + parseInt(a[2]);
    }

    if (a.length == 2) {
        duration = duration + parseInt(a[0]) * 60;
        duration = duration + parseInt(a[1]);
    }

    if (a.length == 1) {
        duration = duration + parseInt(a[0]);
    }
    var h = Math.floor(duration / 3600);
    var m = Math.floor(duration % 3600 / 60);
    var s = Math.floor(duration % 3600 % 60);
    return ((h > 0 ? h + ":" + (m < 10 ? "0" : "") : "") + m + ":" + (s < 10 ? "0" : "") + s);
}


function getOutput(item){

    $(document).ready(function(){
        $('.search-list').on("click",function(){
            var url = "https://www.youtube.com/embed/"+$(this).attr("data-video-id");
            var vtitle = $(this).attr("video-title");
            var vduration = $(this).attr("video-duration");
            console.log(vtitle);
            $.post("/add",{url: url, videoTitle: vtitle, videoDuration: vduration},function(data){});

        });
    });

    var videoId = item.id;
    var title = item.snippet.title;
    var description = item.snippet.description;
    var thumb = item.snippet.thumbnails.high.url;
    var duration = convertTime(item.contentDetails.duration);

    var output = '<li class = "search-list" video-id='+ videoId +' video-title= '+title+' video-duration= '+duration+ ' >' +
                '<div class="list-left">' + 
                '<img src="'+thumb+'">' +
                '</div>' +
				'<div class ="list-right">' + 
				'<h3>'+title+'</h3>' +
				'<p>'+description+'</p>' +
                '<p>'+duration+'</p>' +
				'</div>' +
				'</li>' +
				'<div class="clearfix"></div>' + 
				'';
				
    return output;

}

