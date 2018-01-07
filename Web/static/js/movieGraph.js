
var width = 800,
    height = 620;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-600)
    .linkDistance(60)
    .size([width, height]);

var svg = d3.select(".graph").append("svg")
    .attr("width", width)
    .attr("height", height);

// d3.json("static/graph.json", function(error, graph) {
  
  var abo = "{{ about|safe }}".replace(/u'/g,"'").replace(/'f/g, '"f').replace(/'></g, '"><')
            .replace(/'/g,'"').replace(/"f/g, "'f").replace(/"></g, "'><").replace(/None/g, 'null')
            .replace(/"s/g,"'s").replace(/'star_keyword/g,'"star_keyword')
            .replace(/'score/g,'"score').replace(/'stars/g,'"stars').replace(/'source/g,'"source');
  graph = JSON.parse(abo);
 
  // if (error) throw error;  
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();


  var link = svg.selectAll(".link")
      .data(graph.links)
      .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", 2);

  var tooltip = d3.select("body")
    .append("div")
    .attr("class", "stooltop")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden");


  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      


      .attr("r", function(d) { 
        if (d.rank < 1){ 
          val = 6 }
        else if (d.rank >= 1 && d.rank <1.3) { 
          val = 7 }
        else if (d.rank >= 1.3 && d.rank <1.6) { 
          val = 7 }
        else if (d.rank >= 1.6 && d.rank <1.9) { 
          val = 7 }
        else if (d.rank >= 1.9 && d.rank <2.2) { 
          val = 7 }
        else if (d.rank >= 2.2 && d.rank <2.5) { 
          val = 7 }
        else if (d.rank >= 2.5 && d.rank <2.8) { 
          val = 7 }
        else if (d.rank >= 2.8 && d.rank <3.1) { 
          val = 7 }
        else if (d.rank >= 3.1 && d.rank <3.4) { 
          val = 9 }
        else if (d.rank >= 3.4 && d.rank <3.7) { 
          val = 9 }
        else if (d.rank >= 3.7 && d.rank <4) { 
          val = 10 }
        else if (d.rank >= 4.0 && d.rank <4.3) { 
          val = 11 }
        else if (d.rank >= 4.3 && d.rank <4.7) { 
          val = 12 }
        else if (d.rank >= 4.7 && d.rank <5.0) { 
          val = 12.5 }
        else if (d.rank >= 5.0 && d.rank <5.3) { 
          val = 13 }
        else if (d.rank >= 5.3 && d.rank <5.7) { 
          val = 14 }
        else if (d.rank >= 5.7 && d.rank <5.9) { 
          val = 15 }
        else if (d.rank >= 5.9 && d.rank <6.2) { 
          val = 16 }
        else if (d.rank >= 6.2 && d.rank <6.5) { 
          val = 17 }
        else if (d.rank >= 6.5 && d.rank <6.7) { 
          val = 17 }
        else if (d.rank >= 6.7 && d.rank <6.9) { 
          val = 22 }
        else if (d.rank >= 6.9 && d.rank <7.2) { 
          val = 23 }
        else if (d.rank >= 7.2 && d.rank <7.5) { 
          val = 24 }
        else if (d.rank >= 7.5 && d.rank <7.8) { 
          val = 25 }
        else if (d.rank >= 7.8 && d.rank <8.1) { 
          val = 27 }
        else if (d.rank >= 8.1 && d.rank <8.3) { 
          val = 30 }
        else if (d.rank >= 8.3 && d.rank <8.4) { 
          val = 31 }
        else if (d.rank >= 8.4 && d.rank <8.6) { 
          val = 32 }
        else if (d.rank >= 8.6 && d.rank <8.8) { 
          val = 33 }
        else if (d.rank >= 8.8 && d.rank <9.1) { 
          val = 34 }
        else if (d.rank >= 9.1 && d.rank <9.2) { 
          val = 35 }
        else if (d.rank >= 9.2 && d.rank <9.3) { 
          val = 36 }
        else if (d.rank >= 9.3 && d.rank <9.4) { 
          val = 37 }
        else if (d.rank >= 9.4 && d.rank <9.5) { 
          val = 38 }
        else if (d.rank >= 9.5 && d.rank <9.6) { 
          val = 39 }
        else if (d.rank >= 9.6 && d.rank <9.7) { 
          val = 40 }
        else if (d.rank >= 9.7 && d.rank <9.8) { 
          val = 41 }
        else if (d.rank >= 9.8 && d.rank <9.9) { 
          val = 42 }
        else  { 
          val = 46 };
        return val; })

      .style("fill", function(d) { 

        if (d.rank < 1){ 
          col = "#FE6262" }
        else if (d.rank >= 1 && d.rank <2) { 
          col = "#FE6262" }
        else if (d.rank >= 2 && d.rank <3) { 
          col = "#FE6262" }
        else if (d.rank >= 3 && d.rank <4) { 
          col = "#FE6262" }
        else if (d.rank >= 4 && d.rank <5) { 
          col = "#FE6262" }
        else if (d.rank >= 5 && d.rank <6) { 
          col = "#FF8533" }
        else if (d.rank >= 6 && d.rank <7) { 
          col = "#CCFF33" }
        else if (d.rank >= 7 && d.rank <8) { 
          col = "#66D9FF" }
        else if (d.rank >= 8 && d.rank <9) { 
          col = "#D9007E" }
        else if (d.rank >= 9 && d.rank <10) { 
          col = "#D9007E" }



        return col; })
      .call(force.drag)
      .on("mouseover", function(d){ 
        d3.select(this).style("fill","lightcoral").style('cursor', 'hand');


        return tooltip.style("visibility", "visible").html("<div class='apost'><img src='" + d.poster + "' width='150px' height='200px'></div><p class='aname'>" + d.name + "</p><p class='astar'>" + d.stars + "&nbsp;<span class='arank'>" + d.score + "</font></p><p>" + d.star_keyword  +"</p>"   ) 

        ;})
      .on("mousemove", function(){return tooltip.style("top",
          (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");})
      .on("mouseout", function(){

         d3.select(this)
        .style("fill", function(d) { return color(d.color); });

        return tooltip.style("visibility", "hidden");})
      .on("click", function (d) {  window.open( "/movie/" + d.name_id  ) })






     

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  });
// });

