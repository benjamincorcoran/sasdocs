function createNetworkGraph(json, output){
	
	var nodes = json.nodes
	var links = json.links
	
	var width = 700;
	var height = 500;
	var color = d3.scaleOrdinal(d3.schemePastel2);

	var div = d3.select("body").append("div")	
    .attr("class", "tooltip")				
	.style("opacity", 0);
	
	var labelLayout = d3.forceSimulation(nodes)
		.force("charge", d3.forceManyBody().strength(-50));
		//.force("link", d3.forceLink(links).distance(0).strength(2));
	
	var linkLabelLayout = d3.forceSimulation(links)
		.force("charge", d3.forceManyBody().strength(-50));
	
	var graphLayout = d3.forceSimulation(nodes)
		.force("charge", d3.forceManyBody().strength(-3000))
		.force("center", d3.forceCenter(width / 2, height / 2))
		.force("x", d3.forceX(width / 2).strength(1))
		.force("y", d3.forceY(height / 2).strength(1))
		.force("link", d3.forceLink(links).id(function(d) {return d.id; }).distance(50).strength(1))
		.on("tick", ticked);
		
	var svg = d3.select('#'+output).attr("width", width).attr("height", height);
	var container = svg.append("g");
	
	svg.append("svg:defs").selectAll("marker")
		.data(["end"])      // Different link/path types can be defined here
	  .enter().append("svg:marker")    // This section adds in the arrows
		.attr("id", String)
		.attr("viewBox", "0 -5 10 10")
		.attr("refX", 15)
		.attr("refY", 0)
		.attr("markerWidth", 8)
		.attr("markerHeight", 8)
		.attr("orient", "auto")
		.attr("opacity","0.3")
	  .append("svg:path")
		.attr("d", "M0,-5L10,0L0,5");
	
	svg.call(
		d3.zoom()
			.scaleExtent([.1, 4])
			.on("zoom", function() { container.attr("transform", d3.event.transform); })
	);
	
	var link = container.append("g").attr("class", "links")
		.selectAll("line")
		.data(links)
		.enter()
		.append("line")
		.attr("stroke", "#aaa")
		.attr("stroke-width", "1px")
		.attr("marker-end", "url(#end)");

	var node = container.append("g").attr("class", "nodes")
		.selectAll("g")
		.data(nodes)
		.enter()
		.append("circle")
		.attr("r", 5)
		.attr("fill", function(d) { return color(d.library); })
	
	node.on("mouseover", focus).on("mouseout", unfocus);


	

	node.call(
		d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended)
	);
	
	var labelNode = container.append("g").attr("class", "labelNodes")
		.selectAll("text")
		.data(nodes)
		.enter()
		.append("text")
		.text(function(d, i) { return d.dataset; })
		.style("pointer-events", "none"); // to prevent mouseover/drag capture

	var labelLink = container.append("g").attr("class", "labelLinks")
		.selectAll("text")
		.data(links)
		.enter()
		.append("text")
		.text(function(d, i) { return d.label; })
		.style("fill", "#555")
		.attr("x", function(d) {
			if (d.target.x > d.source.x) {
				return (d.source.x + (d.target.x - d.source.x)/2); }
			else {
				return (d.target.x + (d.source.x - d.target.x)/2); }
		})
		.attr("y", function(d) {
			if (d.target.y > d.source.y) {
				return (d.source.y + (d.target.y - d.source.y)/2); }
			else {
				return (d.target.y + (d.source.y - d.target.y)/2); }
		})
		.style("font-family", "Arial")
		.style("font-size", 12)
		.style("pointer-events", "none"); // to prevent mouseover/drag capture


	var legend = svg.selectAll(".legend")
		.data(color.domain())
		.enter().append("g")
		.attr("class", "legend")
		.attr("library", function(d) {return d;})
		.attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

		legend.append("rect")
			.attr("x", width - 18)
			.attr("width", 18)
			.attr("height", 18)
			.style("fill", color);

		legend.append("text")
			.attr("x", width - 24)
			.attr("y", 9)
			.attr("dy", ".35em")
			.style("text-anchor", "end")
			.text(function(d) { return d; });
			
	legend.on("mouseover", legfocus).on("mouseout", unfocus);

		
	function ticked() {

		node.call(updateNode);
		link.call(updateLink);

		// labelLayout.alphaTarget(0.3).restart();
		labelNode.each(function(d, i) {
			if(i % 2 == 0) {
				d.x = d.x;
				d.y = d.y;
			} else {
				var b = this.getBBox();

				var diffX = d.x - d.x;
				var diffY = d.y - d.y;
				
				var dist = 1 //Math.sqrt(diffX * diffX + diffY * diffY);
				
				var shiftX = b.width * (diffX - dist) / (dist * 2);
				
				shiftX = Math.max(-b.width, Math.min(0, shiftX));
				var shiftY = 16;
				
				this.setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
			}
		});
			
		labelLink.each(function(d, i) {
				var shiftX = (d.target.x - d.source.x)/2 + d.source.x - this.getBBox().width/2;
				var shiftY = (d.target.y - d.source.y)/2 + d.source.y ;

				this.setAttribute("x",shiftX)
				this.setAttribute("y",shiftY)
		});
	
		labelNode.call(updateNode);
		
	}
	function fixna(x) {
		if (isFinite(x)) return x;
		return 0;
	}
	
	var adjlist = [];

	links.forEach(function(d) {
		adjlist[d.source.index + "-" + d.target.index] = true;
		adjlist[d.target.index + "-" + d.source.index] = true;
	});

	function neigh(a, b) {
		return a == b || adjlist[a + "-" + b];
	}
	
	function proc(a,b){
		return a.id == b.source.id || a.id == b.target.id
	}
	

	function focus(d) {
		var index = d3.select(d3.event.target).datum().index;

		div.transition().duration(200).style("opacity", .9);		

		div.html("<b>"+d.library+"."+d.dataset+"</b>\nLine: "+d.line)	
                .style("left", (d3.event.pageX) + "px")		
				.style("top", (d3.event.pageY - 28) + "px");
		
		node.style("opacity", function(o) {
			return neigh(index, o.index) ? 1 : 0.1;
		});
		labelLink.attr("display", function(o) {
		  return proc(d, o) ? "block": "none";
		});
		labelNode.attr("display", function(o) {
		  return neigh(index, o.index) ? "block": "none";
		});
		link.style("opacity", function(o) {
			return o.source.index == index || o.target.index == index ? 1 : 0.1;
		});
	}
	
	function legfocus(d) {
		var library = d3.select(d3.event.target).datum();
		node.style("opacity", function(o) {
			return library==o.library ? 1 : 0.1;
		});
		labelLink.attr("display", function(o) {
		  return library==o.library ? "block": "none";
		});
		labelNode.attr("display", function(o) {
		  return library==o.library ? "block": "none";
		});
		link.style("opacity", function(o) {
			return library==o.source.library && library==o.target.library ? 1 : 0.1;
		});
	}
	
	

	function unfocus() {
	   labelNode.attr("display", "block");
	   labelLink.attr("display", "block");
	   node.style("opacity", 1);
	   link.style("opacity", 1);
	   div.transition().duration(500).style("opacity", 0);	
	}

	function updateLink(link) {
		link.attr("x1", function(d) { return fixna(d.source.x); })
			.attr("y1", function(d) { return fixna(d.source.y); })
			.attr("x2", function(d) { return fixna(d.target.x); })
			.attr("y2", function(d) { return fixna(d.target.y); });
	}

	function updateNode(node) {
		node.attr("transform", function(d) {
			return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
		});
	}

	function dragstarted(d) {
		d3.event.sourceEvent.stopPropagation();
		unfocus()
		node.on("mouseover", null).on("mouseout", null);
		if (!d3.event.active) graphLayout.alphaTarget(0.3).restart();
		d.fx = d.x;
		d.fy = d.y;
	}

	function dragged(d) {
		d.fx = d3.event.x;
		d.fy = d3.event.y;
	}

	function dragended(d) {
		node.on("mouseover", focus).on("mouseout", unfocus);
		if (!d3.event.active) graphLayout.alphaTarget(0);
		d.fx = null;
		d.fy = null;
	}

};


