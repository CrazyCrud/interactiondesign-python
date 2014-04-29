var widths = [10,25,48,60]
var distances = [150,400,600,800]
var results = []

for(var i = 0; i < widths.length; i++){
    for(var j = 0; j < distances.length; j++){
            var result = parseFloat(widths[i] / distances[j]);
            if(results.indexOf(result) > -1){
                $("#results").append("<li>" + result + " of " + widths[i] + "/" + distances[j] + " already in there</li>");
            }else{
                $("#results").append("<li>" + result + " of " + widths[i] + "/" + distances[j] + "</li>");
            }
            results.push(result);
        }
}
