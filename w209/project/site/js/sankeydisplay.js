//user same color scale for both sankeys so we won't have overlap
var color = d3.scale.category20();


function displaysankey(graph, elementid, orientation, valuetype, w, h, passedColorSchemes)
{
    var newColorSchemes = new Array();



    var units = "MkWh";
	if (valuetype == 'percap') {
		units = "kWh per capita";
	}

    var margin = {top: 55, right: 10, bottom: 30, left: 10};
    if (orientation == 'left') {
		margin.right = 5;
	} else {
		margin.left = 5;
	}
	var width = w - margin.left - margin.right,
        height = h - margin.top - margin.bottom;

    var noDecimals = d3.format(",.0f"),    // zero decimal places
		oneDecimals = d3.format(",.1f"),    // zero decimal places
		twoDecimals = d3.format(",.2f"),    // zero decimal places
	    rounding = function(val) { 
			if (val < 100) {
				return val;
			} else if (val < 100000) {
				return Math.round(val/10)*10;
			} else if (val < 1000000) {
				return Math.round(val/100)*100;
			} else if (val < 10000000) {
				return Math.round(val/100)*100;
			} else if (val < 100000000) {
				return Math.round(val/100)*100;
			} else {
				return Math.round(val/1000)*1000;
			}},
        format = function (d) { return twoDecimals((d / divideBy)) + " " + currentUnit; /*return noDecimals(rounding(d)) + " " + units;*/ },
		formatPercent = function(d) { 
			if (d < 0.1) {
				return twoDecimals(d);
			} else {
				return oneDecimals(d);
			}}

    // clear the canvas
    d3.select(elementid).selectAll("*").remove();
    // append the svg canvas to the page
    var svg = d3.select(elementid).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", 
              "translate(" + margin.left + "," + margin.top + ")");

    // Set the sankey diagram properties
    var sankey = null;
    if (orientation == 'left')  {
        sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
            .scaleRight(true)
            .rightHeight(84)
            .leftHeight(height);
    } else {
        sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .size([width, height])
			.scaleLeft(true)
			.rightHeight(height)
			.leftHeight(84);
    }

    var path = sankey.link();
    var nodeMap = {};
	
    graph.nodes.forEach(function(x) { nodeMap[x.name] = x; });
    graph.links = graph.links.map(function(x) {
        return {
            source: nodeMap[x.source],
            target: nodeMap[x.target],
            value: x.value,
			percentage: x.percentage
        };
    });

    sankey
        .nodes(graph.nodes)
        .links(graph.links)
        .layout(0);

    // add in the links
    var link = svg.append("g").selectAll(".link")
        .data(graph.links)
        .enter().append("path")
        .attr("class", "link")
        .attr("d", path)
        .sort(function(a, b) { return b.dy - a.dy; });

    // add the link titles
    link.append("title")
        .text(function(d) {
			if (d.target.right_ghost == 1) {
				return d.source.name + 
			       "\n" + format(d.value) +
				   "\n" + formatPercent(d.percentage) + "%";	
			} else if (d.source.left_ghost == 1) {
				return d.target.name + 
			       "\n" + format(d.value) +
				   "\n" + formatPercent(d.percentage) + "%";
			} else if (orientation == 'left') {
				return d.source.name + " → " + d.target.name + 
			       "\n" + format(d.value) +
				   "\n" + formatPercent(d.percentage) + "% of " +  d.target.name; 
		    } else {
				return d.source.name + " → " + d.target.name + 
			       "\n" + format(d.value) +
				   "\n" + formatPercent(d.percentage) + "% of " +  d.source.name; 
		    }
		   });

    // add in the nodes
    var node = svg.append("g").selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { 
            return "translate(" + d.x + "," + d.y + ")"; });

	// Auxiliary function to determine if node is NOT a PushOut node
	// Used to hide pushout nodes
    function node_notPushout(d) {
        if (orientation == 'left') {
            return !(d.right_ghost == 1);
        } else {
            return !(d.left_ghost == 1);
        }
    }
    
    // add the rectangles for the nodes
    node.append("rect")
        .filter(function(d) { return node_notPushout(d); })   // Don't add text if it is a base node
        .attr("height", function(d) { return Math.max(0, d.dy); })
        .attr("width", sankey.nodeWidth())
        .style("fill", function (d)
        {
            nodeName = d.name; //.replace(/ .*/, "");

            if (typeof passedColorSchemes != "undefined")
            {
                var passedColor = $.grep(passedColorSchemes, function (n, i) {
                    return ( n.name == nodeName );
                });


                if (passedColor.length != 0)
                {
                    newColor = color(nodeName);

                    return passedColor[0].color;
                }

            }

            var newColor = color(nodeName);

            newColorSchemes.push({
                name: nodeName,
                color: newColor
            });

            return d.color = newColor;
        })
        .style("stroke", function(d) { 
            return d3.rgb(d.color).darker(2); })
        // click node to select country/region
        .on("click", function(d)
            {
                // if country or region update selection and update data
                var s = data[d.name];
                if (typeof s != 'undefined' && (s.isregion == 'Y' || s.issubregion == 'Y' || s.iscountry == 'Y'))
                {
                    document.getElementById("region").value = d.name;
                    if (s.iscountry == 'Y')
                    {
                        document.getElementById('hierarchy').value = 'region';
                    }
                    updatedata();
                }
            })
        .append("title")
        .text(function(d) { 
            return d.name + "\n" + format(d.value); })
    ;

    // add in the title for the nodes
   node.append("text")
        .filter(function (d) { return node_notPushout(d); })   // Don't add text if it is a base node
        .attr("x", (orientation == 'left') ? 6 + sankey.nodeWidth() : -6)
        .attr("text-anchor", (orientation == 'left') ? "start" : "end")
        .attr("y", function (d) { return d.dy / 5; })
        .attr("dy", ".35em")
        .attr("transform", null)
        .text(function (d) {
            if (d.name.toLowerCase().indexOf("imbalance") != -1) {
                return d.name + " (?)";
            } else {
                return d.name;
            }
        })
        .attr("font-family", "Montserrat,sans-serif")
        .append("title").text(function(d)  {
            if (d.name.toLowerCase().indexOf("imbalance") != -1) {
                return "These numbers didn't match up";
            } else {
                return "";
            }
        });
            
    //    textG = node.append("a")
    //        .filter(function (d) { return node_notPushout(d); })   // Don't add text if it is a base node
    //    .attr("x", (orientation == 'left') ? 6 + sankey.nodeWidth() : -6)
    //    .attr("y", function (d) { return d.dy / 5; })
    //        .attr("transform", null);


    //textG.append("text")
    //    .filter(function (d) { return node_notPushout(d); })   // Don't add text if it is a base node
    //    .attr("text-anchor", (orientation == 'left') ? "start" : "end")
    //    .attr("dy", ".35em")
    //    .text(function (d) {
    //        if (d.name.toLowerCase().indexOf("imbalance") != -1) {
    //            return d.name + " (?)";
    //        } else {
    //            return d.name;
    //        }
    //    })
    //    .attr("font-family", "Montserrat,sans-serif");

    //textG.append("title").text(function(d)  {
    //        if (d.name.toLowerCase().indexOf("imbalance") != -1) {
    //            return "These numbers didn't match up";
    //        } else {
    //            return "";
    //        }
    //    });

    

    return newColorSchemes;
}
