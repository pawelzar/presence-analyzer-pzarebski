google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});

(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $.getJSON("/api/v1/quarters", function(result){
            var dropdown = $("#quarter_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.quarter_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#quarter_id').change(function(){
            var selected_quarter = $("#quarter_id").val(),
                chart_div = $('#chart_div');
            if(selected_quarter) {
                loading.show();
                chart_div.hide();
                $.getJSON("/api/v1/overtime_in_quarter/"+selected_quarter, function(result){
                    if(result.length === 0) {
                        chart_div.empty();
                        chart_div.append("<p>No overtime hours in this period.</p>");
                        chart_div.show();
                        loading.hide();
                    }
                    else {
                        $.each(result, function(index, value) {
                            value[0] = value[0].name;
                            value[1] = parseInt(value[1]);
                        });
                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'User');
                        data.addColumn('number', 'Overtime hours');
                        data.addRows(result);
                        chart_div.show();
                        loading.hide();
                        var chart = new google.visualization.ColumnChart(chart_div[0]);
                        chart.draw(data);
                    }
                });
            }
            else {
                chart_div.hide();
            }
        });
    });
})(jQuery);
