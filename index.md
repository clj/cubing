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
           {Re-orient cube} Z
           {Match blue pieces} U' .
           {Rotate blue pieces down} R R .
           {Re-orient cube} X X
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

<div class="cube">
<script>
AnimCube3("facelets=LLLLLLRRRLLOLLOLLOLLLLYLLLLWWWWWWWWWLLGLLGLLGLLLLLLBBB&edit=0&hint=7&scale=3&position=lluurrrrrr");
</script>
<div class="caption">Goal</div>
</div>

<div class="cube">
<script>
AnimCube3("facelets=GROORGYOORBWYOORBBYBWYYOWGYYWWWWGBGGOBRWGRGYOBYGWBRBRR&edit=0&hint=7&scale=3&position=lluurrrrrr");
</script>
<div class="caption">Goal</div>
</div>
</body>
</html>