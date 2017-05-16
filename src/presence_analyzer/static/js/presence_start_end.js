google.load("visualization", "1", {packages:["corechart", "timeline"], 'language': 'pl'});

$.getScript("static/js/parse.js");

(function($) {
    $(document).ready(function(){
        var loading = $('#loading'),
            avatar = {};
        $.getJSON("/api/v1/users", function(result){
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name));
                avatar[this.user_id] = this.avatar;
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function(){
            var selected_user = $("#user_id").val(),
                chart_div = $('#chart_div'),
                user_avatar = $('#user_avatar');
            user_avatar.width($("#user_id").width());
            if(selected_user) {
                loading.show();
                chart_div.hide();
                user_avatar.hide();
                $.getJSON("/api/v1/presence_start_end/"+selected_user, function(result){
                })
                .success(function(result){
                    $("#avatar_img").attr("src", avatar[selected_user]);
                    user_avatar.show();
                    $.each(result, function(index, value) {
                        value[1] = parseInterval(value[1]);
                        value[2] = parseInterval(value[2]);
                    });
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Weekday');
                    data.addColumn({ type: 'datetime', id: 'Start' });
                    data.addColumn({ type: 'datetime', id: 'End' });
                    data.addRows(result);
                    var options = {
                        hAxis: {title: 'Weekday'}
                    },
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                    formatter.format(data, 1);
                    formatter.format(data, 2);
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.Timeline(chart_div[0]);
                    chart.draw(data, options);
                })
                .error(function(result){
                    $("#avatar_img").attr("src", avatar[selected_user]);
                    user_avatar.show();
                    chart_div.empty();
                    chart_div.append("<p>No data.</p>");
                    chart_div.show();
                    loading.hide();
                });
            }
            else {
                user_avatar.hide();
                chart_div.hide();
            }
        });
    });
})(jQuery);
