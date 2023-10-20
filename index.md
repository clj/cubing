<html>
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
print_move {Put yellow centre piece on top} X
           {Move right white piece up} R
           {Move bottom white piece up} F F
           {Move left white piece up} L'
           {Re-orient cube} Z Z
           {Prepare last white piece} F
           {Rotate dasy} U'
           {Move final white piece into place} R
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


## Step 2: White Cross

{% cube set start %}
print F:Y FU:W F:O F:G F:R F:W F:B WB WR WG WO
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
AnimCube3("facelets={{ start }}&edit=0&hint=7&scale=3&repeat=0&move={Rotate Blue Down} R2 . {Match Greens} Z' U' . {Rotate Green Down} R2 . {Rotate Red Down} Z' R2 . {Match Blues} Z' U' . {Rotate Blue Down} R2 .");
</script>
<div class="caption">Example Solve</div>
</div>

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