<html>
<title>Cubing</title>
<head>
    <style>
    .cube {
        display: inline-block;
        width: 220px;
        height: 240px;
    }
    .cube .caption {text-align: center; }
    </style>
    <script type="text/javascript" src="js/AnimCube3.js">
    </script>
</head>
<body>

# Cubing

{% cube %}
init GROORGYOORBWYOORBBYBWYYOWGYYWWWWGBGGOBRWGRGYOBYGWBRBRR
# Move the cube into a better starting position
Y
{% endcube %}


## Step 1: Daisy

{% cube set start %}
print F:Y FU:W
{% endcube %}

{% cube set moves %}
print_move {Put yellow centre piece on top} X .
           {Move right white piece up} R .
           {Move bottom white piece up} F F .
           {Move left white piece up} L' .
           {Re-orient cube} Z Z .
           {Prepare last white piece} F' .
           {Rotate dasy} U .
           {Move final white piece into place} L'
{% endcube %}

{% cube set goal %}
print F:Y FU:W
{% endcube %}

<div class="cube">
<script>AnimCube3("facelets={{ goal }}&edit=0");</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>AnimCube3("facelets={{ start }}&edit=0&move={{ moves }}&repeat=0&hint=7&scale=3");</script>
<div class="caption">Example Solve</div>
</div>

The goal for this step is to create the "daisy", a yellow *centre* piece surrounded by white *edge* pieces, without regard for the other colour of the *edge* pieces.





## Step 2: White Cross

{% cube set start %}
print F:Y FU:W F:O F:G F:R F:W F:B WB WR WG WO
{% endcube %}

{% cube set moves %}
print_move {Match orange pieces} U' .
           {Rotate orange pieces down} R R .
           {Match green pieces} U' .
           {Rotate orange pieces down} F F .
           {Rotate red pieces down} L L .
           {Rotate cube} Z
           {Match blue pieces} U' .
           {Rotate blue pieces down} R R .
{% endcube %}

{% cube set goal %}
print F:Y FU:W F:O F:G F:R F:W F:B WB WR WG WO
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&repeat=0&move={{ moves}}");
</script>
<div class="caption">Example Solve</div>
</div>

In this step the white *edge* pieces are moved to surround the white *centre* piece, ensuring that the other colour on the *edge* pieces is positioned with its *centre* piece.





## Step 3: First Layer

{% cube copy first_layer %}

{% cube set start %}
print F:Y FU:W F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

{% cube set moves %}
print_move {Find correctly oriented piece} Z Z .
           {White face on right -> R U R'} R U R' .
           {Rotate cube} Z .
           {Move white fact to top layer -> R U R'} R U R' .
           {Rotate cube} Z' .
           {Orient corner piece} U .
           {White face on left -> L' U' L} L' U' L .
           {Rotate cube} Z Z .
           {Orient corner piece} U .
           {White face on right -> R U R'} R U R' .
           {Move and orient white face to top layer -> 2x L' U' L} L' U' L . L' U' L . .
           {Orient corner piece} U .
           {White face on left -> L' U' L} L' U' L .
{% endcube %}

{% cube set goal %}
print F:Y FU:W F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>
</body>
</html>

### Algorithm

{% cube [first_layer] set fl_start %}
U Z
print F:Y FU:W F:O F:G F:R F:W F:B FRU:WGR FRU:W
{% endcube %}

{% cube [first_layer] set fl_moves %}
print_move {1: Orient top layer correctly} U' .
            {2: Rotate cube correctly} Z .
            {3: Apply algorithm - R U R'} R U R' .
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ fl_start }}&edit=0&hint=7&scale=3&move={{ fl_moves }}");
</script>
<div class="caption">Example Solve</div>
</div>
</body>
</html>


* Find a corner piece with a white face on the top layer facing outwards
    1. Turn the top layer layer to position the corner piece in the correct orientation
    2. Rotate the cube so that the white face of the corner piece faces left or right and the centre piece matching the corner colour faces towards you
    3. Apply the correct algorithm:
        * If white face is facing left: L' U' L
        * If white face is facing right: R U R'
* If there are no white faces on the top layer facing outwards
    * Find top corner piece where the white face is facing up
        1. Orient the white face to face outwards:
            * If the corner is on the left: L' U' L OR L' U L ???
            * If white face is facing right: R U R'
    * Find a bottom corner piece that is not in the correct position


## Step 4: Second Layer

{% cube set start %}
print F:Y FU:W~Y FU:B~Y FU:G~Y FU:R~Y FU:O~Y FU:Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

{% cube set moves %}
print_move {Rotate ...} Z' .
           {Orient top} U' .
           {U + Right trigger - U R U R'} U R U R' .
           {Fix ...} U' Z L' U' L .
           {Rotate ...} Z Z
           {U + Right trigger - U R U R'} U R U R' .
           {Fix ...} U' Z L' U' L .
           {Rotate ...} Z Z
           {Orient top} U U .
           {U + Right trigger - U R U R'} U R U R' .
           {Fix ...} U' Z L' U' L .
           # Expand this to more steps?
           {Displace ...} Z' L' U' L . L' U' L . U U Z' . R U R'
           {Rotate ...} Z
           {Orient top} U U .
           {U' + Left trigger - U' L' U' L} U' L' U' L .
           {Fix ...} U Z' R U R' .
{% endcube %}

{% cube set goal %}
print F:Y FU:W~Y FU:B~Y FU:G~Y FU:R~Y FU:O~Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>




## Step 5: Yellow Cross

{% cube set start %}
print F:Y FU:W~Y FU:B~Y FU:G~Y FU:R~Y FU:O~Y FU:Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

{% cube set moves %}
print_move {Rotate ...} Z Z
           {F R U R' U' F'} F R U R' U' F' .
           {F R U R' U' F'} F R U R' U' F' .
{% endcube %}

{% cube set goal %}
print F:Y FU:W~Y FU:B~Y FU:G~Y FU:R~Y FU:O~Y FU:Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>




## Step 6: Yellow Edges

{% cube set start %}
print F:Y FU:W FU:B FU:G FU:R FU:O FU:Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

{% cube set moves %}
print_move {Rotate } Z'
           {Swap left - R U R' U R U2 R' U} R U R' U R U2 R' U
           {Rotate } Z
           {Swap left - R U R' U R U2 R' U} R U R' U R U2 R' U
{% endcube %}

{% cube set goal %}
print F:Y FU:W FU:B FU:G FU:R FU:O FU:Y F:O F:G F:R F:W F:B FRU:W* WB WR WG WO
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>




## Step 7: Position Yellow Corners

{% cube set start %}
print
{% endcube %}

{% cube set moves %}
print_move {Get a corner in correct position} U R U' L' U R' U' L .
           {Rotate ...} Z'
           {Cycle the three other corners} U R U' L' U R' U' L .
{% endcube %}

{% cube set goal %}
print
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>




## Step 8: Orient Yellow Corners

{% cube set start %}
print
{% endcube %}

{% cube set moves %}
print_move {4x} R' D' R D . R' D' R D . R' D' R D . R' D' R D . .
           {Move new corner into place} U
           {4x} R' D' R D . R' D' R D . R' D' R D . R' D' R D . .
           {Move new corner into place} U
           {4x} R' D' R D . R' D' R D . R' D' R D . R' D' R D . .
           {Rotate top}
           U U
{% endcube %}

{% cube set goal %}
print
{% endcube %}

<div class="cube">
<script>
AnimCube3("facelets={{ goal }}&edit=0&hint=7&scale=3");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&move={{ moves }}");
</script>
<div class="caption">Example Solve</div>
</div>
</body>
</html>
