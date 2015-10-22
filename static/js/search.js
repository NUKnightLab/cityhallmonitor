var summaryTemplate = null;
var resultTemplate = null;

$(function() {
    summaryTemplate = _.template($("#summary-template").html());
    resultTemplate = _.template($("#result-template").html());
    $('.example-search').click(function() {
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });
    buildDateUI();
});

var addResult = function(obj) {
    $.each(obj.docs, function(i, doc) {
        $(resultTemplate(doc)).appendTo('#search-results');
    });
};

var doSearch = function(subscribeUrl) {
    showLoadingState();
    var DATE_FORMAT = 'YYYY-MM-DD 00:00:00+00:00';
    var MONTH_FORMAT = 'YYYY-MM';
    var dateRangeType = $('#date-range-type').val();
    var query = $('#search-input').val();
    var startDate = moment();
    var endDate = moment();
    var queryExtra = '';
    var queryQualifier = '';
    switch (dateRangeType) {
        case 'past-year':
            startDate.subtract(1, 'years');
            var iterDate = moment();
            while (iterDate.format(MONTH_FORMAT) >= startDate.format(MONTH_FORMAT)) { 
                queryExtra += ' MatterSortMonth: ' + iterDate.format(MONTH_FORMAT);
                iterDate.subtract(1, 'months');
            }
            queryQualifier = ' in the past year';
            break;
        case 'past-month':
            startDate.subtract(30, 'days');
            queryExtra += 'MatterSortMonth: ' + startDate.format(MONTH_FORMAT);
            if (endDate.format(MONTH_FORMAT) !== startDate.format(MONTH_FORMAT)) {
                queryExtra += ' MatterSortMonth: ' + endDate.format(MONTH_FORMAT);
            }
            queryQualifier = ' in the last 30 days';
            break;
        case 'any':
            // no queryExtra for all dates
            break;
    }
    query += ' account:12872-knight-lab project:"Chicago City Hall Monitor"';
    query += ' ' + queryExtra;
    console.log('EXECUTING DOCUMENTCLOUD QUERY:: ' + query);
    $.ajax({
        url: 'https://www.documentcloud.org/api/search.json?q='
        + query + '&per_page=1000&data=true'
    })
    .success(function(data) {
        var groups = {};
        var dates = [];
        var startDateStr = startDate.format(DATE_FORMAT);
        var dt = null;
        $.each(data.documents, function(i, doc) {
            dt = doc.data.MatterSortDate;
            if (dateRangeType !== 'any' && dt < startDateStr) {
                return true;
            }
            
            if(dates.indexOf(dt) < 0) {        
                dates.push(dt);
                groups[dt] = {};
            }
            
            if(doc.data.MatterId in groups[dt]) {
                groups[dt][doc.data.MatterId]['docs'].push(doc);
            } else {
                groups[dt][doc.data.MatterId] = {
                    'data': doc.data,
                    'docs': [doc]
                };
            }            
        });

        $('#results-summary').html($(summaryTemplate({
            total:data.total,
            query: $('#search-input').val(),
            qualifier: queryQualifier
        })));

        $('#search-subscribe-form').submit(function(event) {
            handle_subscribe(event, subscribeUrl);
            return false;
        });

        if(data.documents.length) {
            dates.sort(function(a,b) { return (b < a) ? -1 : 1 });
            for (i=0; i<dates.length; i++) {
                var dateGroups = groups[dates[i]];               
                $.each(dateGroups, function(j, g) {
                    addResult(g);
                });
            }
        }
        $("#search-results").foundation('reveal', 'reflow');
        hideLoadingState();
    });
}; // doSearch
