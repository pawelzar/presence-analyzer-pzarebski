google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});

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
            if(selected_user) {
                loading.show();
                chart_div.hide();
                user_avatar.hide();
                $.getJSON("/api/v1/presence_weekday/"+selected_user, function(result){
                })
                .success(function(result){
                    $("#avatar_img").attr("src", avatar[selected_user]);
                    user_avatar.show();
                    var data = google.visualization.arrayToDataTable(result),
                        options = {};
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.PieChart(chart_div[0]);
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
        });
    });
})(jQuery);
