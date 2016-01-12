var summaryTemplate = null;
var singleResultTemplate = null;
var multiResultTemplate = null;
var resultStatsTemplate = null;

$(function() {
    summaryTemplate = _.template($("#summary-template").html());
    singleResultTemplate = _.template($("#single-result-template").html());
    multiResultTemplate = _.template($("#multi-result-template").html());
    resultStatsTemplate = _.template($("#result-stats-sidebar").html());
    $('.example-search').click(function() {
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });
    buildDateUI();
});

var appendResult = function(obj) {
    var statusClass;
    switch (obj.docs[0].matter.status){
        case 'Adopted':
        case 'Approved':
        case 'Passed':
        case 'Recommended for Passage':
            statusClass = 'success';
            break;

        case 'Deferred and Published':
        case 'Direct Introduction':
        case 'In Committee':
        case 'Introduced':
        case 'Placed on File':
        case 'Recommended for Re-referral':
        case 'Re-referred':
            statusClass = 'warning';
            break;

        case 'Failed to Pass':
        case 'Recommended Do Not Pass':
        case 'Tabled':
        case 'Vetoed':
        case 'Void':
        case 'Withdrawn':
            statusClass = 'alert';
            break;
    }
    if(obj.docs.length > 1) {
        $(multiResultTemplate({docs: obj.docs, statusClass: statusClass})).appendTo('#search-results');
    } else {
        $(singleResultTemplate({doc: obj.docs[0], statusClass: statusClass})).appendTo('#search-results');
    }
};

//Need to store the results of the AJAX call somewhere so we can sort without hitting the database
var documents;

var doSearch = function(searchUrl, subscribeUrl) {
    showLoadingState();
    documents = [];
    var query = $('#search-input').val();
    var dateRangeType = $('#date-range-type').val();
    var ignoreRoutine = $('#ignore-routine').is(':checked');
    var queryQualifier = '';
    var isRanked = false;
    // only rank if not the default query
    if (subscribeUrl != null) {
      var isRanked = true;
    }

    //build up summary stats for sidebar
    function buildResultStats(doc, statsData){
        var statTypes = {
            'Statuses': 'status',
            'Matter Types': 'type'
        };
        $.each(statTypes, function(key, matter_field) {
            if (!(key in statsData)){
                statsData[key] = {};
            }
            if(doc.matter[matter_field] in statsData[key]) {
                statsData[key][doc.matter[matter_field]] += 1;
            } else {
                statsData[key][doc.matter[matter_field]] = 1;
            }
        });
        return statsData;
    };

    function appendSummaryAndStats(total, qualifier, statsData){
        $('#results-summary').html($(summaryTemplate({
            total: total,
            query: $('#search-input').val(),
            qualifier: qualifier
        })));
        if (statsData) {
            $('#results-stats').html(resultStatsTemplate({statsData: statsData}));
        }
    };

    function createResultMeta(data){
        var groups = {};
        var dates = [];
        var statsData = {};
        $.each(data.documents, function(i, doc) {
            // dt is datetime
            var dt = doc.sort_date;
            // if the datetime hasn't already been added to the dates array
            if(dates.indexOf(dt) < 0) {
                dates.push(dt);
                groups[dt] = {};
            }
            // if the datetime already exists in `groups`, it means the matter has multiple documents: add docs to existing attribute
            // otherwise just create the `docs` property
            if(doc.matter.id in groups[dt]) {
                groups[dt][doc.matter.id]['docs'].push(doc);
            } else {
                groups[dt][doc.matter.id] = {
                    'docs': [doc]
                };
            }
            buildResultStats(doc, statsData);
        });
        appendSummaryAndStats(data.documents.length, queryQualifier, statsData);
        return {
          documents: data.documents,
          groups: groups,
          dates: dates
        };
    }

    // group documents with their related matters
    function appendMatters(data, groups, dates){
        if(data.documents.length > 0) {
            dates.sort(function(a,b) { return (b < a) ? -1 : 1 });
            for (i=0; i<dates.length; i++) {
                var dateGroups = groups[dates[i]];
                $.each(dateGroups, function(j, g) {
                    appendResult(g);
                });
            }
        }
    };

    function showEmailForm(){
      $('#search-subscribe-form, #sort-by').show();
          $('#search-subscribe-form').submit(function(event) {
              handle_subscribe(event, subscribeUrl);
              return false;
          });
    };

    //used to determine language to display and time period to return
    switch (dateRangeType) {
        case 'past-year':
            queryQualifier = ' in the past year';
            break;

        case 'past-month':
            queryQualifier = ' in the last 30 days';
            break;

        case 'any':
            break;
    }

    console.log('EXECUTING QUERY:: ' + query + ", is_ranked: " +isRanked );
    $.ajax({
        url: searchUrl,
        data: {
            query: query,
            date_range: dateRangeType,
            ignore_routine: ignoreRoutine,
            is_ranked: isRanked
        }
    })
    .success(function(data) {
        console.log(data);

        var resultMeta = createResultMeta(data);
        documents = resultMeta.documents;
        var groups = resultMeta.groups;
        var dates = resultMeta.dates;

        appendMatters(data, groups, dates);

        // don't let people subscribe to the default query
        if (subscribeUrl != null) {
          showEmailForm(subscribeUrl);
        }
        $("#search-results").foundation('reveal', 'reflow');

    })
    .error(function(xhr, status, errMsg) {
        alert(errMsg);
    })
    .complete(function(xhr, status) {
        hideLoadingState();
    });
}; // doSearch

var sortByDate = function(){
  $('#sort-chron').on('click', function(){
    console.log(documents);
  });
}
