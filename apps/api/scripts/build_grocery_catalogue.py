#!/usr/bin/env python3
"""One-off builder for ``app/demo_catalogue_grocery.json`` (the fictional grocery / fresh-food demo stores)."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'app' / 'demo_catalogue_grocery.json'
UA = 'PayFoundDemoCatalogue/1.0 (limziyang5119@gmail.com; one-off build script)'
SEARCH = 'https://world.openfoodfacts.org/cgi/search.pl'

# (OFF category tag, pool, price range cents, emoji, items to keep)
OFF_QUERIES = [
    ('pastas', 'pantry', (129, 429), '🍝', 14), ('rices', 'pantry', (199, 899), '🍚', 10),
    ('breakfast-cereals', 'pantry', (299, 649), '🥣', 14), ('biscuits', 'pantry', (149, 449), '🍪', 12),
    ('chocolates', 'pantry', (149, 599), '🍫', 12), ('canned-foods', 'pantry', (99, 399), '🥫', 16),
    ('sauces', 'pantry', (199, 599), '🥫', 12), ('jams', 'pantry', (249, 549), '🍯', 8),
    ('peanut-butters', 'pantry', (299, 649), '🥜', 6), ('potato-crisps', 'snack', (199, 449), '🥔', 12),
    ('instant-noodles', 'pantry', (79, 349), '🍜', 10), ('nuts', 'snack', (349, 999), '🥜', 10),
    ('honeys', 'pantry', (399, 899), '🍯', 6), ('olive-oils', 'pantry', (699, 1699), '🫒', 6),
    ('flours', 'pantry', (199, 549), '🌾', 6), ('sugars', 'pantry', (199, 449), '🍬', 6),
    ('soups', 'pantry', (199, 449), '🥣', 8), ('condiments', 'pantry', (199, 499), '🧂', 10),
    ('spices', 'pantry', (249, 699), '🌶️', 8), ('cookies', 'snack', (199, 499), '🍪', 8),
    ('popcorn', 'snack', (199, 399), '🍿', 4), ('snack-bars', 'snack', (249, 599), '🍫', 8),
    ('frozen-foods', 'frozen', (349, 999), '🧊', 14), ('ice-creams', 'frozen', (399, 799), '🍨', 8),
    ('carbonated-drinks', 'drink', (99, 349), '🥤', 12), ('waters', 'drink', (79, 349), '💧', 10),
    ('fruit-juices', 'drink', (249, 599), '🧃', 10), ('coffees', 'drink', (599, 1499), '☕', 8),
    ('teas', 'drink', (299, 799), '🍵', 8), ('energy-drinks', 'drink', (199, 399), '⚡', 6),
    ('iced-teas', 'drink', (149, 349), '🧋', 6), ('plant-based-milks', 'drink', (299, 599), '🥛', 6),
]

# (name, price_cents, shelf_life_hours, emoji, description)
PRODUCE = [
    ('Bananas (per kg)', 179, 96, '🍌', 'Ripe yellow bananas sold by the kilo.'),
    ('Gala Apples (per kg)', 349, 336, '🍎', 'Crisp, sweet eating apples.'),
    ('Hass Avocados (each)', 129, 96, '🥑', 'Ripe-and-ready avocados.'),
    ('Roma Tomatoes (per kg)', 299, 120, '🍅', 'Firm plum tomatoes for sauces and salads.'),
    ('Cherry Tomatoes 250 g', 229, 120, '🍅', 'Sweet vine cherry tomatoes.'),
    ('Cucumbers (each)', 99, 168, '🥒', 'Crunchy salad cucumbers.'),
    ('Baby Spinach 142 g', 299, 96, '🥬', 'Washed baby spinach leaves.'),
    ('Curly Kale (per bunch)', 249, 96, '🥬', 'Fresh curly kale bunch.'),
    ('Carrots 1 kg', 169, 336, '🥕', 'Whole carrots, 1 kg bag.'),
    ('Yellow Onions 1 kg', 149, 504, '🧅', 'All-purpose yellow onions.'),
    ('Red Onions (per kg)', 219, 504, '🧅', 'Mild red onions.'),
    ('Garlic (3 bulbs)', 129, 504, '🧄', 'Firm garlic bulbs.'),
    ('Fresh Ginger (per 100 g)', 89, 336, '🫚', 'Fresh ginger root.'),
    ('Russet Potatoes 2 kg', 349, 504, '🥔', 'Baking and mashing potatoes.'),
    ('Sweet Potatoes (per kg)', 249, 336, '🍠', 'Orange-fleshed sweet potatoes.'),
    ('Broccoli Crown (each)', 189, 120, '🥦', 'Fresh green broccoli crown.'),
    ('Cauliflower (each)', 279, 168, '🥦', 'Whole white cauliflower.'),
    ('Red Bell Peppers (each)', 119, 168, '🫑', 'Sweet red peppers.'),
    ('Zucchini (per kg)', 259, 120, '🥒', 'Tender green zucchini.'),
    ('Button Mushrooms 227 g', 229, 96, '🍄', 'Fresh white mushrooms.'),
    ('Lemons (each)', 69, 336, '🍋', 'Juicy lemons.'),
    ('Limes (each)', 59, 336, '🍋', 'Fresh limes.'),
    ('Navel Oranges 1.5 kg', 449, 336, '🍊', 'Sweet seedless oranges.'),
    ('Strawberries 454 g', 449, 72, '🍓', 'Ripe strawberries, 454 g punnet.'),
    ('Blueberries 170 g', 399, 96, '🫐', 'Plump blueberries.'),
    ('Seedless Grapes (per kg)', 499, 168, '🍇', 'Green seedless grapes.'),
    ('Mango (each)', 199, 96, '🥭', 'Ripe sweet mango.'),
    ('Pineapple (each)', 399, 120, '🍍', 'Whole golden pineapple.'),
    ('Watermelon (half)', 449, 96, '🍉', 'Half seedless watermelon.'),
    ('Cantaloupe (each)', 349, 96, '🍈', 'Fragrant orange melon.'),
    ('Peaches (per kg)', 429, 72, '🍑', 'Soft yellow peaches.'),
    ('Conference Pears (per kg)', 379, 168, '🍐', 'Firm eating pears.'),
    ('Fresh Basil (per bunch)', 199, 72, '🌿', 'Fragrant basil bunch.'),
    ('Fresh Cilantro (per bunch)', 129, 72, '🌿', 'Fresh cilantro bunch.'),
    ('Flat Parsley (per bunch)', 129, 96, '🌿', 'Flat-leaf parsley bunch.'),
    ('Fresh Mint (per bunch)', 149, 72, '🌿', 'Fresh mint bunch.'),
    ('Spring Onions (per bunch)', 109, 120, '🧅', 'Bunch of spring onions.'),
    ('Romaine Hearts (2 pack)', 299, 120, '🥬', 'Crisp romaine lettuce hearts.'),
    ('Iceberg Lettuce (each)', 169, 168, '🥬', 'Whole iceberg lettuce.'),
    ('Green Cabbage (each)', 219, 336, '🥬', 'Dense green cabbage.'),
    ('Celery (each)', 189, 168, '🥬', 'Fresh celery bunch.'),
    ('Sweetcorn (2 cobs)', 169, 72, '🌽', 'Fresh sweetcorn on the cob.'),
    ('Green Beans 250 g', 229, 96, '🫛', 'Trimmed green beans.'),
    ('Asparagus (per bunch)', 349, 72, '🌱', 'Slender green asparagus.'),
    ('Eggplant (each)', 169, 120, '🍆', 'Glossy purple eggplant.'),
    ('Butternut Squash (each)', 299, 504, '🎃', 'Sweet butternut squash.'),
    ('Beetroot (per bunch)', 249, 168, '🫜', 'Fresh beetroot bunch.'),
    ('Radishes (per bunch)', 139, 96, '🌱', 'Peppery radish bunch.'),
    ('Leeks (2 pack)', 249, 168, '🌱', 'Fresh leeks.'),
    ('Pomegranate (each)', 249, 336, '🍎', 'Ruby pomegranate.'),
    ('Kiwi Fruit (4 pack)', 229, 168, '🥝', 'Ripe green kiwi fruit.'),
    ('Papaya (each)', 349, 96, '🍈', 'Ripe orange papaya.'),
    ('Red Chillies 100 g', 119, 168, '🌶️', 'Fresh red chillies.'),
    ('Sugar Snap Peas 200 g', 299, 96, '🫛', 'Sweet, crisp snap peas.'),
    ('Bok Choy (each)', 179, 96, '🥬', 'Fresh bok choy.'),
    ('Rocket Salad 100 g', 249, 72, '🥬', 'Peppery rocket leaves.'),
    ('Mixed Salad Bag 200 g', 279, 96, '🥗', 'Washed mixed salad leaves.'),
    ('Fresh Figs (4 pack)', 399, 72, '🫐', 'Soft ripe figs.'),
    ('Cherries 300 g', 549, 72, '🍒', 'Dark sweet cherries.'),
]
MEAT = [
    ('Chicken Breast Fillets (per kg)', 999, 96, '🍗', 'Skinless chicken breast, sold by weight.'),
    ('Chicken Thighs Bone-In (per kg)', 599, 96, '🍗', 'Bone-in chicken thighs.'),
    ('Whole Chicken 1.6 kg', 1199, 96, '🐔', 'Whole free-range chicken.'),
    ('Chicken Drumsticks 1 kg', 599, 96, '🍗', 'Tray of chicken drumsticks.'),
    ('Beef Mince 500 g', 749, 72, '🥩', 'Lean beef mince, 500 g.'),
    ('Ribeye Steak (each)', 1699, 96, '🥩', 'Marbled ribeye steak, about 300 g.'),
    ('Sirloin Steak (each)', 1399, 96, '🥩', 'Sirloin steak, about 250 g.'),
    ('Beef Short Ribs (per kg)', 1499, 96, '🥩', 'Meaty beef short ribs.'),
    ('Pork Chops (2 pack)', 799, 96, '🥩', 'Bone-in pork chops.'),
    ('Pork Belly Slices 500 g', 899, 96, '🥓', 'Sliced pork belly.'),
    ('Italian-Style Sausages (6 pack)', 699, 96, '🌭', 'Herbed pork sausages.'),
    ('Lamb Chops (4 pack)', 1599, 96, '🍖', 'Trimmed lamb chops.'),
    ('Lamb Mince 500 g', 849, 72, '🍖', 'Lamb mince, 500 g.'),
    ('Streaky Bacon 250 g', 599, 240, '🥓', 'Smoked streaky bacon.'),
    ('Sliced Ham 150 g', 399, 168, '🍖', 'Thin-sliced cooked ham.'),
    ('Turkey Mince 500 g', 699, 72, '🦃', 'Lean turkey mince.'),
    ('Chicken Wings 1 kg', 749, 96, '🍗', 'Tray of chicken wings.'),
    ('Beef Burger Patties (4 pack)', 899, 96, '🍔', 'Hand-pressed beef patties.'),
    ('Diced Stewing Beef 500 g', 899, 96, '🥩', 'Diced beef for slow cooking.'),
    ('Chorizo Ring 225 g', 549, 480, '🌭', 'Cured paprika chorizo.'),
]
SEAFOOD = [
    ('Salmon Fillet (per kg)', 2499, 48, '🐟', 'Skin-on salmon fillet.'),
    ('Cod Fillet (per kg)', 2299, 48, '🐟', 'Thick white cod fillet.'),
    ('Sea Bass Fillets (2 pack)', 1199, 48, '🐟', 'Fresh sea bass fillets.'),
    ('Raw King Prawns 400 g', 1299, 48, '🦐', 'Peeled raw king prawns.'),
    ('Mussels (per kg)', 699, 36, '🦪', 'Live mussels, cleaned.'),
    ('Squid Tubes 300 g', 799, 48, '🦑', 'Cleaned squid tubes.'),
    ('Tuna Steak (each)', 1099, 36, '🐟', 'Sashimi-grade tuna steak.'),
    ('Whole Rainbow Trout (each)', 749, 48, '🐟', 'Gutted whole trout.'),
    ('Sea Scallops (6 pack)', 1499, 36, '🦪', 'Hand-dived scallops.'),
    ('Cooked Crab Meat 200 g', 1299, 72, '🦀', 'Picked white and brown crab meat.'),
    ('Fresh Sardines 500 g', 599, 36, '🐟', 'Whole fresh sardines.'),
    ('Mackerel Fillets (2 pack)', 649, 48, '🐟', 'Fresh mackerel fillets.'),
    ('Smoked Salmon 100 g', 699, 336, '🐟', 'Sliced cold-smoked salmon.'),
    ('Haddock Fillet (per kg)', 1999, 48, '🐟', 'Fresh haddock fillet.'),
    ('Oysters (6 pack)', 1499, 36, '🦪', 'Fresh shucking oysters.'),
]
BAKERY = [
    ('Sourdough Loaf', 599, 72, '🍞', 'Slow-fermented sourdough, baked this morning.'),
    ('French Baguette', 349, 24, '🥖', 'Crisp-crusted baguette.'),
    ('Multigrain Loaf', 549, 72, '🍞', 'Seeded multigrain sandwich loaf.'),
    ('Wholemeal Loaf', 499, 96, '🍞', 'Stone-ground wholemeal loaf.'),
    ('Brioche Burger Buns (6 pack)', 449, 72, '🍔', 'Soft glazed brioche buns.'),
    ('Butter Croissant', 349, 24, '🥐', 'Flaky all-butter croissant.'),
    ('Pain au Chocolat', 399, 24, '🥐', 'Laminated pastry with dark chocolate.'),
    ('Cinnamon Roll', 429, 36, '🥮', 'Iced cinnamon roll.'),
    ('Blueberry Muffin', 349, 48, '🧁', 'Fresh-baked blueberry muffin.'),
    ('Plain Bagels (4 pack)', 499, 72, '🥯', 'Boiled-and-baked bagels.'),
    ('Rosemary Focaccia', 599, 48, '🫓', 'Olive-oil focaccia with rosemary.'),
    ('Ciabatta Rolls (4 pack)', 449, 48, '🥖', 'Airy ciabatta rolls.'),
    ('Dark Rye Loaf', 549, 120, '🍞', 'Dense dark rye loaf.'),
    ('Garlic Flatbreads (3 pack)', 399, 72, '🫓', 'Soft garlic flatbreads.'),
    ('Fruit Scones (2 pack)', 399, 36, '🥧', 'Butter scones with sultanas.'),
    ('Sausage Roll', 349, 24, '🥐', 'Flaky pastry sausage roll.'),
    ('Almond Danish', 429, 24, '🥐', 'Almond frangipane danish.'),
    ('Banana Bread Loaf', 699, 96, '🍌', 'Moist banana loaf.'),
    ('Victoria Sponge Cake', 1899, 72, '🍰', 'Jam and cream sponge, serves 8.'),
    ('New York Cheesecake Slice', 549, 48, '🍰', 'Baked vanilla cheesecake slice.'),
    ('Double Chocolate Brownies (4 pack)', 599, 96, '🍫', 'Fudgy chocolate brownies.'),
    ('Oat & Raisin Cookies (6 pack)', 549, 120, '🍪', 'Chewy oat and raisin cookies.'),
    ('Lemon Tart', 499, 48, '🥧', 'Buttery lemon tart.'),
    ('Pistachio Baklava (6 pack)', 899, 168, '🥮', 'Honey-soaked baklava.'),
    ('Glazed Doughnuts (4 pack)', 599, 24, '🍩', 'Yeast-raised glazed doughnuts.'),
    ('Naan Bread (4 pack)', 399, 96, '🫓', 'Soft oven-baked naan.'),
    ('Pita Bread (6 pack)', 349, 96, '🫓', 'Pocket pita breads.'),
    ('Flour Tortillas (8 pack)', 399, 168, '🌮', 'Soft flour tortillas.'),
    ('Seeded Crackers 200 g', 449, 480, '🍘', 'House-baked seeded crackers.'),
    ('Pecan Pie Slice', 479, 72, '🥧', 'Maple pecan pie slice.'),
]
DAIRY = [
    ('Whole Milk 1 L', 189, 120, '🥛', 'Fresh pasteurised whole milk.'),
    ('Whole Milk 2 L', 329, 120, '🥛', 'Fresh pasteurised whole milk, 2 L.'),
    ('Semi-Skimmed Milk 2 L', 319, 120, '🥛', 'Fresh semi-skimmed milk.'),
    ('Lactose-Free Milk 1 L', 249, 168, '🥛', 'Lactose-free whole milk.'),
    ('Salted Butter 250 g', 449, 480, '🧈', 'Churned salted butter.'),
    ('Mature Cheddar 400 g', 649, 720, '🧀', 'Aged cheddar block.'),
    ('Mozzarella Ball 125 g', 199, 240, '🧀', 'Fresh mozzarella in brine.'),
    ('Greek Feta 200 g', 349, 480, '🧀', 'Barrel-aged feta.'),
    ('Parmesan Wedge 150 g', 599, 720, '🧀', 'Hard aged parmesan.'),
    ('Brie Wheel 200 g', 549, 240, '🧀', 'Soft ripened brie.'),
    ('Goat Cheese Log 150 g', 479, 240, '🧀', 'Creamy goat cheese.'),
    ('Greek Yogurt 500 g', 349, 240, '🥣', 'Thick strained Greek yogurt.'),
    ('Plain Yogurt 1 kg', 399, 240, '🥣', 'Natural set yogurt.'),
    ('Kefir 500 ml', 349, 168, '🥛', 'Cultured kefir drink.'),
    ('Cream Cheese 200 g', 329, 336, '🧀', 'Soft cream cheese.'),
    ('Heavy Cream 250 ml', 349, 168, '🥛', 'Pouring double cream.'),
    ('Sour Cream 200 ml', 229, 240, '🥣', 'Cultured sour cream.'),
    ('Free-Range Eggs 12-Pack', 499, 480, '🥚', 'Large free-range eggs, a dozen.'),
    ('Free-Range Eggs 6-Pack', 279, 480, '🥚', 'Large free-range eggs, half dozen.'),
    ('Cottage Cheese 300 g', 299, 168, '🥣', 'Small-curd cottage cheese.'),
    ('Ricotta 250 g', 349, 168, '🧀', 'Fresh ricotta.'),
    ('Halloumi 225 g', 449, 480, '🧀', 'Squeaky grilling cheese.'),
    ('Skyr Natural 450 g', 399, 240, '🥣', 'High-protein skyr.'),
    ('Chocolate Milk 500 ml', 229, 168, '🥛', 'Cold chocolate milk.'),
    ('Ghee 250 g', 699, 2000, '🧈', 'Clarified butter.'),
    ('Unsalted Butter 250 g', 449, 480, '🧈', 'Churned unsalted butter.'),
    ('Oat Cream 250 ml', 279, 240, '🥛', 'Dairy-free cooking cream.'),
]
HEALTH = [
    ('Hand Sanitiser 100 ml', 299, 'Alcohol hand gel.', '🧴'), ('Adhesive Plasters (40 pack)', 349, 'Assorted-size plasters.', '🩹'),
    ('Vitamin C Tablets (60)', 799, 'Daily vitamin C supplement.', '💊'), ('Lip Balm SPF 15', 249, 'Moisturising lip balm.', '💄'),
    ('Fluoride Toothpaste 100 ml', 349, 'Daily fluoride toothpaste.', '🪥'), ('Soft Toothbrush (2 pack)', 299, 'Soft-bristle toothbrushes.', '🪥'),
    ('Gentle Shampoo 400 ml', 599, 'Everyday shampoo.', '🧴'), ('Sunscreen SPF 50 150 ml', 1099, 'Water-resistant sunscreen.', '☀️'),
    ('Digital Thermometer', 1299, 'Fast-read digital thermometer.', '🌡️'), ('Cotton Pads (100)', 249, 'Soft cotton pads.', '🧴'),
    ('Saline Nasal Spray 30 ml', 549, 'Saline nasal rinse spray.', '🧴'), ('Aloe Vera Gel 200 ml', 699, 'Soothing after-sun gel.', '🌿'),
    ('Multivitamin Gummies (60)', 1199, 'Adult multivitamin gummies.', '💊'), ('Electrolyte Sachets (10)', 899, 'Rehydration drink sachets.', '🧃'),
    ('Face Masks (10 pack)', 599, 'Disposable face masks.', '😷'), ('Body Lotion 250 ml', 799, 'Fragrance-free body lotion.', '🧴'),
    ('Dental Floss 50 m', 249, 'Waxed dental floss.', '🪥'), ('Deodorant Roll-On 50 ml', 449, 'All-day deodorant.', '🧴'),
    ('Throat Lozenges (24)', 399, 'Honey-lemon lozenges.', '🍯'), ('First Aid Kit (small)', 1599, 'Compact first aid kit.', '🧰'),
    ('Soap Bar (3 pack)', 399, 'Mild glycerin soap bars.', '🧼'), ('Tissues (6 boxes)', 549, 'Soft facial tissues.', '🧻'),
    ('Eye Drops 10 ml', 899, 'Lubricating eye drops.', '👁️'), ('Insect Repellent 100 ml', 799, 'Skin-safe repellent spray.', '🦟'),
    ('Steel Water Bottle 600 ml', 1499, 'Reusable steel bottle.', '🧴'), ('Hair Ties (20 pack)', 249, 'Soft elastic hair ties.', '🎀'),
]
HOUSEHOLD = [
    ('Dish Soap 500 ml', 349, 'Grease-cutting washing-up liquid.', '🧼'), ('Laundry Detergent 1.5 L', 1199, 'Concentrated liquid detergent.', '🧺'),
    ('Kitchen Roll (4 pack)', 649, 'Absorbent kitchen towels.', '🧻'), ('Bin Bags 30 L (40)', 549, 'Tie-handle bin bags.', '🗑️'),
    ('Sponge Scourers (6 pack)', 349, 'Dual-sided scrub sponges.', '🧽'), ('LED Bulb E27 (2 pack)', 599, 'Warm white 9 W LED bulbs.', '💡'),
    ('AA Batteries (8 pack)', 799, 'Alkaline AA batteries.', '🔋'), ('Soy Wax Candle', 1099, 'Unscented soy candle.', '🕯️'),
    ('Glass Food Containers (3)', 1999, 'Lidded oven-safe containers.', '🥡'), ('Cotton Tea Towels (2)', 899, 'Absorbent cotton tea towels.', '🧺'),
    ('All-Purpose Cleaner 750 ml', 449, 'Multi-surface spray cleaner.', '🧴'), ('Toilet Paper (12 roll)', 899, 'Soft 2-ply tissue.', '🧻'),
    ('Baking Paper Roll', 349, 'Non-stick baking parchment.', '📜'), ('Foil Wrap 10 m', 349, 'Kitchen aluminium foil.', '📜'),
    ('Clothes Pegs (50)', 299, 'Plastic clothes pegs.', '🧺'), ('Mop Refill Head', 799, 'Microfibre mop head.', '🧹'),
    ('Dishwasher Tablets (30)', 1299, 'All-in-one dishwasher tablets.', '🧼'), ('Reusable Shopping Bag', 249, 'Foldable tote.', '🛍️'),
    ('Glass Cleaner 500 ml', 399, 'Streak-free spray.', '🧴'), ('Matches (10 boxes)', 199, 'Household safety matches.', '🔥'),
    ('Plant Pot 15 cm', 699, 'Terracotta pot with saucer.', '🪴'), ('Extension Lead 4-way', 1499, 'Surge-protected 2 m extension.', '🔌'),
    ('Rubber Gloves (M)', 349, 'Latex-free washing-up gloves.', '🧤'), ('Scented Laundry Beads', 899, 'Fabric freshening beads.', '🧺'),
    ('Storage Jars (4 pack)', 1499, 'Airtight glass jars.', '🫙'), ('Dustpan & Brush Set', 799, 'Compact dustpan and brush.', '🧹'),
]
# Restaurant menus: (name, price, shelf life h, emoji, description)
MENUS = {
    'pizzeria': [
        ('Margherita Pizza 12 in', 1299, 6, '🍕', 'Tomato, mozzarella and basil on a wood-fired base.'),
        ('Pepperoni Pizza 12 in', 1499, 6, '🍕', 'Wood-fired pizza with spicy pepperoni.'),
        ('Four Cheese Pizza 12 in', 1499, 6, '🍕', 'Mozzarella, cheddar, parmesan and goat cheese.'),
        ('Garden Veggie Pizza 12 in', 1399, 6, '🍕', 'Peppers, mushrooms, olives and red onion.'),
        ('Spaghetti Bolognese', 1199, 8, '🍝', 'Slow-cooked beef ragu on spaghetti.'),
        ('Baked Lasagne', 1299, 12, '🍝', 'Layered pasta, beef ragu and bechamel.'),
        ('Mac & Cheese Bake', 999, 12, '🧀', 'Three-cheese baked macaroni.'),
        ('Caesar Salad', 999, 8, '🥗', 'Romaine, parmesan, croutons and dressing.'),
        ('Garlic Dough Balls (8)', 599, 6, '🧄', 'Warm dough balls with garlic butter.'),
        ('Tiramisu Pot', 649, 36, '🍰', 'Coffee-soaked sponge and mascarpone.'),
        ('Calzone Prosciutto', 1499, 6, '🥟', 'Folded pizza with ham and ricotta.'),
        ('Penne Arrabbiata', 1099, 8, '🍝', 'Spicy tomato penne.'),
        ('Minestrone Soup', 799, 24, '🥣', 'Vegetable and bean soup.'),
        ('Chicken Parmigiana', 1599, 8, '🍗', 'Breaded chicken, tomato and mozzarella.'),
        ('Caprese Salad', 899, 8, '🥗', 'Tomato, mozzarella and basil.'),
    ],
    'noodle': [
        ('Beef Pho', 1399, 6, '🍜', 'Rice noodles in star-anise beef broth.'),
        ('Pork Ramen', 1499, 6, '🍜', 'Rich pork broth, noodles, egg and greens.'),
        ('Vegetable Ramen', 1299, 6, '🍜', 'Miso broth with tofu and mushrooms.'),
        ('Chicken Pad Thai', 1299, 6, '🍝', 'Wok-fried rice noodles with peanuts.'),
        ('Pork Dumplings (8)', 899, 12, '🥟', 'Steamed pork and cabbage dumplings.'),
        ('Veggie Dumplings (8)', 849, 12, '🥟', 'Steamed vegetable dumplings.'),
        ('Egg Fried Rice', 899, 8, '🍚', 'Wok-fried rice with egg and spring onion.'),
        ('Chicken Katsu Curry', 1399, 8, '🍛', 'Crumbed chicken with Japanese curry.'),
        ('Seafood Laksa', 1499, 6, '🍜', 'Coconut curry broth with prawns.'),
        ('Spring Rolls (6)', 649, 12, '🥟', 'Crisp vegetable spring rolls.'),
        ('Teriyaki Salmon Bowl', 1599, 8, '🍣', 'Glazed salmon over rice with greens.'),
        ('Salmon Sushi Box (12)', 1699, 8, '🍣', 'Nigiri and maki selection.'),
        ('Miso Soup', 399, 12, '🥣', 'Tofu and seaweed miso soup.'),
        ('Mapo Tofu Rice', 1199, 8, '🍛', 'Spicy tofu with minced pork over rice.'),
        ('Sesame Noodle Salad', 999, 12, '🥗', 'Cold noodles with sesame dressing.'),
    ],
    'saffron': [
        ('Butter Chicken & Rice', 1499, 8, '🍛', 'Creamy tomato chicken curry with basmati.'),
        ('Lamb Rogan Josh', 1699, 8, '🍛', 'Slow-cooked lamb in Kashmiri spices.'),
        ('Chana Masala', 1199, 12, '🍛', 'Chickpeas in spiced tomato sauce.'),
        ('Palak Paneer', 1299, 10, '🍛', 'Spinach curry with paneer.'),
        ('Chicken Tikka Wrap', 1099, 6, '🌯', 'Tandoori chicken, salad and mint yogurt.'),
        ('Falafel Wrap', 999, 6, '🌯', 'Falafel, hummus and pickles in flatbread.'),
        ('Lamb Shawarma Plate', 1599, 6, '🥙', 'Sliced lamb with rice and salad.'),
        ('Hummus & Warm Pita', 699, 24, '🫓', 'Creamy hummus with warm pita.'),
        ('Tabbouleh Salad', 799, 12, '🥗', 'Parsley, bulgur and lemon salad.'),
        ('Vegetable Samosas (3)', 549, 10, '🥟', 'Spiced potato and pea samosas.'),
        ('Mango Lassi', 449, 24, '🥭', 'Chilled yogurt and mango drink.'),
        ('Dal Tadka', 1099, 12, '🍛', 'Yellow lentils with garlic tempering.'),
        ('Garlic Naan', 349, 8, '🫓', 'Tandoor-baked garlic naan.'),
        ('Chicken Biryani', 1499, 8, '🍛', 'Layered spiced rice and chicken.'),
        ('Baba Ganoush', 649, 24, '🍆', 'Smoky roasted eggplant dip.'),
    ],
    'night': [
        ('Chicken Satay (6 skewers)', 999, 6, '🍢', 'Grilled skewers with peanut sauce.'),
        ('Nasi Lemak', 1099, 8, '🍚', 'Coconut rice, sambal, egg, peanuts and cucumber.'),
        ('Char Kway Teow', 1199, 6, '🍜', 'Wok-fried flat noodles with prawns.'),
        ('Beef Rendang & Rice', 1499, 10, '🍛', 'Slow-braised coconut beef.'),
        ('Roti Canai with Curry', 799, 6, '🫓', 'Flaky flatbread with dhal curry.'),
        ('Pork Banh Mi', 999, 6, '🥖', 'Pickles, herbs and grilled pork in a baguette.'),
        ('Crispy Chicken Bao (2)', 899, 6, '🥟', 'Steamed buns with fried chicken.'),
        ('Korean Fried Chicken', 1399, 6, '🍗', 'Double-fried wings, gochujang glaze.'),
        ('Bibimbap Bowl', 1399, 8, '🍚', 'Rice, vegetables, egg and gochujang.'),
        ('Tom Yum Soup', 999, 8, '🥣', 'Hot and sour prawn soup.'),
        ('Green Papaya Salad', 899, 8, '🥗', 'Crunchy lime-chilli salad.'),
        ('Takoyaki (8)', 849, 6, '🐙', 'Octopus balls with sauce and bonito.'),
        ('Mango Sticky Rice', 749, 12, '🥭', 'Coconut sticky rice and ripe mango.'),
        ('Vegetable Curry Puff (3)', 599, 8, '🥟', 'Crisp pastry with curried potato.'),
        ('Iced Thai Tea', 449, 12, '🧋', 'Sweet spiced milk tea over ice.'),
    ],
    'cafe': [
        ('Flat White', 450, 1, '☕', 'Double espresso with silky milk.'),
        ('Oat Milk Latte', 500, 1, '☕', 'Espresso with steamed oat milk.'),
        ('Cold Brew Coffee', 500, 24, '☕', 'Slow-steeped iced coffee.'),
        ('Matcha Latte', 550, 1, '🍵', 'Ceremonial-grade matcha with milk.'),
        ('Chai Latte', 500, 1, '☕', 'Spiced tea with steamed milk.'),
        ('Fresh Orange Juice 330 ml', 549, 24, '🍊', 'Squeezed to order.'),
        ('Green Smoothie 400 ml', 699, 12, '🥤', 'Spinach, apple, banana and ginger.'),
        ('Berry Smoothie 400 ml', 699, 12, '🥤', 'Mixed berries, banana and yogurt.'),
        ('Avocado Toast', 1099, 4, '🥑', 'Sourdough, smashed avocado and chilli.'),
        ('Egg & Bacon Roll', 799, 4, '🥪', 'Free-range egg and bacon in a soft roll.'),
        ('Granola Yogurt Pot', 599, 24, '🥣', 'Greek yogurt, granola and berries.'),
        ('Chicken Club Sandwich', 1099, 6, '🥪', 'Toasted club with bacon and mayo.'),
        ('Quinoa Salad Box', 1199, 10, '🥗', 'Quinoa, roasted veg and feta.'),
        ('Tomato Soup & Bread', 899, 12, '🥣', 'Roast tomato soup with sourdough.'),
        ('Carrot Cake Slice', 549, 36, '🍰', 'Cream-cheese-frosted carrot cake.'),
        ('Iced Americano', 400, 1, '☕', 'Espresso over ice and water.'),
        ('Hot Chocolate', 479, 1, '☕', 'Dark hot chocolate.'),
        ('Bubble Milk Tea', 599, 4, '🧋', 'Black milk tea with tapioca pearls.'),
        ('Ham & Cheese Toastie', 799, 4, '🥪', 'Toasted sourdough, ham and cheddar.'),
        ('Fruit Salad Cup', 549, 24, '🍓', 'Cut seasonal fruit.'),
    ],
}
DRINK_EMOJI = {'☕', '🍵', '🧋', '🥤', '🍊'}

# Street spots in San Francisco (fictional businesses). Neutral names: no SF neighbourhood words.
SPOTS = [
    ('1288 Haight St', 37.7699, -122.4455), ('3320 Mission St', 37.7425, -122.4228), ('2040 Irving St', 37.7636, -122.4790),
    ('455 Clement St', 37.7829, -122.4635), ('3881 24th St', 37.7517, -122.4283), ('1912 Fillmore St', 37.7871, -122.4334),
    ('850 Irving St', 37.7640, -122.4660), ('4001 Judah St', 37.7609, -122.5057), ('1730 Divisadero St', 37.7878, -122.4399),
    ('901 Valencia St', 37.7561, -122.4210), ('2650 Geary Blvd', 37.7821, -122.4504), ('1700 Polk St', 37.7936, -122.4219),
    ('310 Columbus Ave', 37.7983, -122.4087), ('1550 Stockton St', 37.8010, -122.4094), ('2250 Chestnut St', 37.8002, -122.4415),
    ('1 Ferry Building Plaza', 37.7955, -122.3937), ('1000 Potrero Ave', 37.7556, -122.4067), ('2800 3rd St', 37.7517, -122.3880),
    ('500 Portola Dr', 37.7382, -122.4495), ('4600 Mission St', 37.7213, -122.4345), ('5200 3rd St', 37.7283, -122.3930),
    ('2700 Ocean Ave', 37.7326, -122.4767), ('3200 Taraval St', 37.7425, -122.4989), ('1500 Noriega St', 37.7541, -122.4811),
    ('400 Castro St', 37.7617, -122.4350), ('200 Church St', 37.7677, -122.4290), ('1200 Folsom St', 37.7728, -122.4122),
    ('600 Brannan St', 37.7743, -122.4012), ('1801 Bush St', 37.7861, -122.4285), ('1100 Hyde St', 37.7915, -122.4177),
    ('50 Bayshore Blvd', 37.7410, -122.4040), ('1600 Geneva Ave', 37.7120, -122.4180), ('3400 Sacramento St', 37.7881, -122.4478),
    ('1000 Sloat Blvd', 37.7340, -122.4900), ('2300 Mariposa St', 37.7633, -122.4015), ('5 Terry Francois Blvd', 37.7717, -122.3912),
    ('390 Hyde St', 37.7848, -122.4160), ('1400 Judah St', 37.7620, -122.4720), ('700 Bay St', 37.8050, -122.4180),
    ('1200 Cabrillo St', 37.7747, -122.4720), ('2100 Lombard St', 37.7993, -122.4370), ('900 Taraval St', 37.7431, -122.4690),
    ('3300 Fulton St', 37.7740, -122.4950),
]

# id, slug, name, merchant category, emoji, kind, hours profile, fulfilment min, second branch?, products, description
STORES = [
    ('m14', 'cedar-row-pantry', 'Cedar Row Pantry', 'Grocery', '🛒', 'grocer', 'grocer', 20, True, 38, 'Everyday groceries, pantry staples and fresh basics.'),
    ('m15', 'harbour-greens', 'Harbour Greens', 'Greengrocer', '🥬', 'greengrocer', 'market', 15, True, 36, 'Daily-delivered fruit, vegetables and herbs.'),
    ('m16', 'crumb-and-co-bakery', 'Crumb & Co Bakery', 'Bakery', '🥐', 'bakery', 'bakery', 10, True, 32, 'Small-batch breads and pastries baked every morning.'),
    ('m17', 'night-market-kitchen', 'Night Market Kitchen', 'Restaurant & café', '🍢', 'night', 'night', 25, False, 26, 'Late-night street-food classics, cooked to order.'),
    ('m18', 'ironwood-butcher', 'Ironwood Butcher', 'Butcher & fishmonger', '🥩', 'butcher', 'butcher', 20, False, 30, 'Local-style butchery and ready-to-cook cuts.'),
    ('m19', 'silver-net-fishmonger', 'Silver Net Fishmonger', 'Butcher & fishmonger', '🐟', 'fish', 'butcher', 20, False, 22, 'Daily fish and shellfish, filleted on request.'),
    ('m20', 'meadowbank-dairy', 'Meadowbank Dairy', 'Dairy', '🥛', 'dairy', 'market', 15, False, 28, 'Milk, cheese, eggs and cultured dairy.'),
    ('m21', 'lamp-post-convenience', 'Lamp Post Convenience', 'Convenience', '🏪', 'convenience', '24h', 10, True, 36, 'Open-all-hours essentials, snacks and drinks.'),
    ('m22', 'half-moon-corner-shop', 'Half Moon Corner Shop', 'Convenience', '🌙', 'convenience', '24h', 10, False, 32, 'Late-night corner shop with fresh basics.'),
    ('m23', 'orchard-and-vine', 'Orchard & Vine', 'Greengrocer', '🍎', 'greengrocer', 'market', 15, False, 34, 'Orchard fruit, salad and seasonal veg.'),
    ('m24', 'saffron-table', 'Saffron Table', 'Restaurant & café', '🍛', 'saffron', 'restaurant', 30, False, 24, 'Home-style curries, wraps and mezze.'),
    ('m25', 'brick-oven-pizzeria', 'Brick Oven Pizzeria', 'Restaurant & café', '🍕', 'pizzeria', 'restaurant', 25, True, 26, 'Wood-fired pizza and pasta, ready to collect.'),
    ('m26', 'bean-and-leaf-cafe', 'Bean & Leaf Café', 'Restaurant & café', '☕', 'cafe', 'cafe', 10, True, 28, 'Coffee, juices, sandwiches and cakes.'),
    ('m27', 'noodle-lantern', 'Noodle Lantern', 'Restaurant & café', '🍜', 'noodle', 'restaurant', 25, False, 26, 'Noodle bowls, dumplings and rice dishes.'),
    ('m28', 'early-rise-bakehouse', 'Early Rise Bakehouse', 'Bakery', '🍞', 'bakery', 'bakery', 10, False, 28, 'Sourdough, bagels and morning bakes.'),
    ('m29', 'rye-and-rose-patisserie', 'Rye & Rose Patisserie', 'Bakery', '🍰', 'patisserie', 'cafe', 10, False, 22, 'Cakes, tarts and celebration bakes.'),
    ('m30', 'corner-larder', 'Corner Larder', 'Grocery', '🧺', 'grocer', 'grocer', 20, False, 34, 'Neighbourhood grocer with a deli counter.'),
    ('m31', 'parkside-provisions', 'Parkside Provisions', 'Grocery', '🛍️', 'grocer', 'long', 20, True, 36, 'Groceries, drinks and ready-to-eat lunches.'),
    ('m32', 'fernway-fresh-market', 'Fernway Fresh Market', 'Grocery', '🥦', 'grocer', 'long', 20, False, 40, 'Fresh produce, dairy and pantry in one stop.'),
    ('m33', 'lantern-lane-grocer', 'Lantern Lane Grocer', 'Grocery', '🏮', 'grocer', 'grocer', 20, False, 32, 'Family-run grocer with international staples.'),
    ('m34', 'green-stall-produce', 'Green Stall Produce', 'Greengrocer', '🍅', 'greengrocer', 'market', 15, False, 30, 'Open-air-style fruit and veg stall.'),
    ('m35', 'hollow-creek-farm-stand', 'Hollow Creek Farm Stand', 'Greengrocer', '🥕', 'greengrocer', 'market', 15, False, 28, 'Farm-direct produce, eggs and honey.'),
    ('m36', 'smoke-and-cleaver', 'Smoke & Cleaver', 'Butcher & fishmonger', '🌭', 'butcher', 'butcher', 20, False, 26, 'Butcher, smokehouse and sausage makers.'),
    ('m37', 'churn-and-curd', 'Churn & Curd', 'Dairy', '🧀', 'dairy', 'market', 15, False, 24, 'Cheese counter, yogurt and farm eggs.'),
    ('m38', 'birch-wellness-pharmacy', 'Birch Wellness Pharmacy', 'Pharmacy', '💊', 'pharmacy', 'pharmacy', 15, True, 24, 'Everyday health, personal care and wellness items.'),
    ('m39', 'plain-goods-household', 'Plain Goods Household', 'Household', '🧽', 'household', 'household', 20, False, 28, 'Cleaning, kitchen and home basics.'),
    ('m40', 'sunrise-grab-and-go', 'Sunrise Grab & Go', 'Convenience', '🌅', 'convenience', 'long', 10, True, 34, 'Breakfast, lunch and snacks to go.'),
]

HOURS = {  # weekday 0=Mon .. 6=Sun ; empty list = closed
    '24h': ('24 hours', {d: [('00:00', '24:00')] for d in range(7)}),
    'long': ('06:00–23:00', {d: [('06:00', '23:00')] for d in range(7)}),
    'grocer': ('07:00–22:00', {d: [('07:00', '22:00')] for d in range(7)}),
    'market': ('07:00–19:00', {**{d: [('07:00', '19:00')] for d in range(6)}, 6: [('08:00', '16:00')]}),
    'bakery': ('06:00–15:00', {**{d: [('06:00', '15:00')] for d in range(1, 7)}, 0: []}),
    'butcher': ('08:00–19:00', {**{d: [('08:00', '19:00')] for d in range(6)}, 6: []}),
    'restaurant': ('11:00–22:30', {d: [('11:00', '14:30'), ('17:00', '22:30')] for d in range(7)}),
    'night': ('17:00–02:00', {d: [('17:00', '02:00')] for d in range(7)}),
    'cafe': ('07:00–17:00', {d: [('07:00', '17:00')] for d in range(7)}),
    'pharmacy': ('08:00–21:00', {d: [('08:00', '21:00')] for d in range(7)}),
    'household': ('09:00–19:00', {**{d: [('09:00', '19:00')] for d in range(6)}, 6: [('10:00', '17:00')]}),
}

RECIPES = {  # store kind -> (pool, count) ; pools: pantry snack frozen drink produce meat seafood bakery dairy menu cafe health household
    'grocer': [('pantry', 12), ('drink', 5), ('dairy', 5), ('produce', 6), ('bakery', 3), ('snack', 4), ('frozen', 3), ('meat', 2)],
    'greengrocer': [('produce', 30), ('dairy', 2), ('drink', 2), ('pantry', 2)],
    'bakery': [('bakery', 24), ('cafe', 5), ('dairy', 2)],
    'patisserie': [('bakery', 14), ('cafe', 6), ('dairy', 2)],
    'butcher': [('meat', 18), ('seafood', 4), ('dairy', 3), ('pantry', 3)],
    'fish': [('seafood', 15), ('meat', 2), ('produce', 3), ('pantry', 2)],
    'dairy': [('dairy', 22), ('bakery', 2), ('drink', 3), ('pantry', 1)],
    'convenience': [('snack', 9), ('drink', 9), ('pantry', 6), ('dairy', 4), ('bakery', 2), ('frozen', 3), ('household', 3)],
    'pizzeria': [('menu', 15), ('drink', 6), ('bakery', 2)],
    'noodle': [('menu', 15), ('drink', 6)],
    'saffron': [('menu', 15), ('drink', 5)],
    'night': [('menu', 15), ('drink', 6)],
    'cafe': [('menu', 20), ('bakery', 4), ('drink', 3)],
    'pharmacy': [('health', 24)],
    'household': [('household', 24), ('pantry', 3)],
}
MUST = {  # items carried by many stores so cross-store comparison works (same catalogue key)
    'grocer': ['Whole Milk 1 L', 'Bananas (per kg)', 'Free-Range Eggs 12-Pack'],
    'greengrocer': ['Bananas (per kg)', 'Gala Apples (per kg)', 'Hass Avocados (each)'],
    'dairy': ['Whole Milk 1 L', 'Free-Range Eggs 12-Pack', 'Salted Butter 250 g'],
    'convenience': ['Whole Milk 1 L', 'Free-Range Eggs 6-Pack', 'Bananas (per kg)'],
    'bakery': ['Sourdough Loaf', 'Butter Croissant'],
}
MENU_FOR = {'cafe': 'cafe', 'pizzeria': 'pizzeria', 'noodle': 'noodle', 'saffron': 'saffron', 'night': 'night'}


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def metres(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(h))


def unit_of(name):
    m = re.search(r'\((per [^)]+)\)', name)
    if m:
        return m.group(1)
    return 'each' if '(each)' in name else 'pack'


def fetch_off(tag, count):
    params = {'action': 'process', 'tagtype_0': 'categories', 'tag_contains_0': 'contains', 'tag_0': tag,
              'tagtype_1': 'countries', 'tag_contains_1': 'contains', 'tag_1': 'united-states',
              'sort_by': 'unique_scans_n', 'page_size': str(max(60, count * 5)), 'json': '1',
              'fields': 'code,product_name,brands,quantity'}
    req = urllib.request.Request(SEARCH + '?' + urllib.parse.urlencode(params), headers={'User-Agent': UA})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode('utf-8')).get('products', [])
        except Exception as exc:  # network failures are retried, then skipped
            print('  retry', tag, exc, file=sys.stderr)
            time.sleep(4)
    return []


def generic_name(product):
    """Strip brand words, keep a plain English product name plus pack size; None when unusable."""
    name = (product.get('product_name') or '').strip()
    qty = (product.get('quantity') or '').strip()
    if not name or not name.isascii() or not qty.isascii():
        return None
    for brand in re.split(r'[,;]', product.get('brands') or ''):
        brand = brand.strip()
        if len(brand) >= 2:
            name = re.sub(re.escape(brand), ' ', name, flags=re.I)
    name = re.sub(r'\b\d+\s*(x|×)\s*\d*', ' ', name, flags=re.I)
    name = re.sub(r'\b\d+([.,]\d+)?\s*(g|kg|ml|cl|l|oz|fl\.?\s*oz|lb)\b', ' ', name, flags=re.I)
    name = re.split(r'\s[-–]\s', name)[0]
    name = re.sub(r"[^A-Za-z&' -]+", ' ', name)
    name = re.sub(r'\b(No|Nr|N)\b', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip(' -')
    if len(name) < 4 or len(name) > 44 or len(name.split()) > 6:
        return None
    if name.isupper() or name.islower():
        name = name.title()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|cl|l|oz|lb)', qty.lower().replace(',', '.'))
    if not m or float(m.group(1)) <= 0:
        return None
    number = m.group(1)[:-2] if m.group(1).endswith('.0') else m.group(1)
    return f'{name} {number} {m.group(2)}'


def build_off(cache_path, offline):
    cache = json.loads(cache_path.read_text()) if cache_path and cache_path.exists() else {}
    cache = {k: v for k, v in cache.items() if v}  # never trust an empty (failed) response
    if not offline:
        for round_ in range(14):  # search.pl is rate-limited and sometimes returns 503; retry the gaps
            missing = [q for q in OFF_QUERIES if q[0] not in cache]
            if not missing:
                break
            if round_:
                print(f'{len(missing)} queries missing; waiting before retry', file=sys.stderr)
                time.sleep(20)
            for tag, _pool, _price, _emoji, keep in missing:
                print('fetching', tag, file=sys.stderr)
                raw = fetch_off(tag, keep)
                if raw:
                    cache[tag] = raw
                    if cache_path:
                        cache_path.write_text(json.dumps(cache))
                time.sleep(6)  # polite: Open Food Facts allows ~10 search requests per minute
    items, seen = [], set()
    for tag, pool, (lo, hi), emoji, keep in OFF_QUERIES:
        raw = cache.get(tag)
        taken = 0
        for p in raw or []:
            name = generic_name(p)
            key = slug(name) if name else None
            if not name or key in seen:
                continue
            seen.add(key)
            h = int(hashlib.sha1(key.encode()).hexdigest()[:8], 16)
            price = (lo + h % max(1, hi - lo + 1)) // 10 * 10 + 9
            items.append({'name': name, 'key': key, 'pool': pool, 'price_cents': price, 'emoji': emoji,
                          'off_code': str(p.get('code') or ''), 'off_category': tag})
            taken += 1
            if taken >= keep:
                break
    return items


WEB_PUBLIC = Path(__file__).resolve().parents[2] / 'web' / 'public'
PRODUCT_IMAGES = WEB_PUBLIC / 'images' / 'products'
CREDITS = WEB_PUBLIC / 'image-credits-grocery.json'
TILE = {'Groceries': '#f3efe6', 'Drinks': '#e9f1f5', 'Fresh produce': '#e8f3e6', 'Meat & seafood': '#f6e9e6',
        'Bakery': '#f7eedd', 'Dairy & eggs': '#eef1f6', 'Ready meals': '#f6ece4', 'Home & living': '#eeeeea',
        'Health & personal care': '#eaf2f1'}


PENDING_TILES = {}


def illustration_path(category, emoji):
    """Shared illustrated tile (WebP, emoji drawn large on a neutral category tint), one per category+emoji."""
    name = 'illus-' + slug(category) + '-' + '-'.join(f'{ord(c):x}' for c in emoji if ord(c) != 0xFE0F) + '.webp'
    if not (PRODUCT_IMAGES / name).exists():
        PENDING_TILES[name] = (category, emoji)
    return '/images/products/' + name


def render_tiles():
    """Rasterise missing tiles with headless Chromium (needs playwright + Pillow), then store as WebP."""
    if not PENDING_TILES:
        return
    from io import BytesIO
    from PIL import Image
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 400, 'height': 400}, device_scale_factor=1)
        for name, (category, emoji) in PENDING_TILES.items():
            page.set_content(f'<body style="margin:0"><div style="width:400px;height:400px;background:{TILE.get(category, "#f0f0ee")};'
                             f'display:flex;align-items:center;justify-content:center;font-size:190px;line-height:1;'
                             f'font-family:\'Apple Color Emoji\',\'Segoe UI Emoji\',\'Noto Color Emoji\',sans-serif">{emoji}</div></body>')
            Image.open(BytesIO(page.screenshot(clip={'x': 0, 'y': 0, 'width': 400, 'height': 400}))).convert('RGB').save(
                PRODUCT_IMAGES / name, 'WEBP', quality=82, method=6)
        browser.close()
    PENDING_TILES.clear()


def api_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:
            print('  retry', url[-40:], exc, file=sys.stderr)
            time.sleep(4)
    return None


def fetch_front_image(code, meta_cache):
    """(image bytes, credit dict) of the product's front photo at 400 px from Open Food Facts, or None."""
    if code not in meta_cache:
        data = api_json(f'https://world.openfoodfacts.org/api/v2/product/{code}?fields=code,image_front_url,images')
        product = (data or {}).get('product') or {}
        url = product.get('image_front_url')
        uploader = None
        m = re.search(r'/(front_[a-z]+)\.\d+\.\d+\.jpg', url or '')
        if m:
            imgid = (product.get('images') or {}).get(m.group(1), {}).get('imgid')
            uploader = ((product.get('images') or {}).get(str(imgid)) or {}).get('uploader')
        meta_cache[code] = {'url': url, 'uploader': uploader}
        time.sleep(1.2)
    meta = meta_cache[code]
    if not meta['url']:
        return None
    req = urllib.request.Request(meta['url'], headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read(), meta
    except Exception as exc:
        print('  image download failed', code, exc, file=sys.stderr)
        return None


def to_webp(raw, dest):
    from io import BytesIO
    from PIL import Image
    img = Image.open(BytesIO(raw)).convert('RGB')
    img.thumbnail((360, 360))
    canvas = Image.new('RGB', (400, 400), (255, 255, 255))
    canvas.paste(img, ((400 - img.width) // 2, (400 - img.height) // 2))
    canvas.save(dest, 'WEBP', quality=78, method=6)


def add_images(products, cache_dir):
    """Download each Open Food Facts front photo once (CC BY-SA); everything else gets an illustrated category tile."""
    PRODUCT_IMAGES.mkdir(parents=True, exist_ok=True)
    meta_path = cache_dir / 'image_meta.json'
    meta_cache = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    photos, by_code = {}, {}
    for p in products:
        if p.get('off_code'):
            by_code.setdefault(p['off_code'], []).append(p)
    for i, (code, items) in enumerate(sorted(by_code.items()), 1):
        dest = PRODUCT_IMAGES / f'off-{code}.webp'
        if code in meta_cache and not meta_cache[code]['url'] and not dest.exists():
            continue
        if not dest.exists():
            got = fetch_front_image(code, meta_cache)
            meta_path.write_text(json.dumps(meta_cache))
            if not got:
                continue
            to_webp(got[0], dest)
        meta = meta_cache.get(code) or fetch_front_image(code, meta_cache)[1]
        photos[code] = {'file': f'/images/products/off-{code}.webp', 'product_code': code,
                        'source_url': f'https://world.openfoodfacts.org/product/{code}', 'original_image_url': meta['url'],
                        'contributor': meta.get('uploader') or 'Open Food Facts contributors',
                        'licence': 'CC BY-SA 3.0', 'licence_url': 'https://creativecommons.org/licenses/by-sa/3.0/',
                        'adaptation': 'Resized to fit a 400 px white square and converted to WebP. Shared alike under CC BY-SA.',
                        'products': [x['id'] for x in items]}
        if i % 25 == 0:
            print('  images', i, '/', len(by_code), file=sys.stderr)
    counts = {'photo': 0, 'illustration': 0}
    illustrations = {}
    for p in products:
        photo = photos.get(p.get('off_code'))
        if photo:
            p['image_url'], p['image_kind'] = photo['file'], 'photo'
            counts['photo'] += 1
        else:
            p['image_url'], p['image_kind'] = illustration_path(p['category'], p['emoji']), 'illustration'
            illustrations[p['image_url']] = {'category': p['category'], 'emoji': p['emoji']}
            counts['illustration'] += 1
    render_tiles()
    CREDITS.write_text(json.dumps({
        'note': 'Photographs of packaged items come from Open Food Facts (https://world.openfoodfacts.org) and are licensed CC BY-SA 3.0 by their contributors; they were downloaded once at build time and are served from this site, never hotlinked. Every other grocery item uses an original illustrated category tile (an emoji on a neutral background) and is not a photograph. Product names and pack sizes come from the Open Food Facts database (ODbL 1.0). Stores, prices and stock are fictional.',
        'photo_source': {'name': 'Open Food Facts', 'url': 'https://world.openfoodfacts.org',
                         'database_licence': 'ODbL 1.0', 'image_licence': 'CC BY-SA 3.0'},
        'photos': sorted(photos.values(), key=lambda x: x['product_code']),
        'illustrations': {'description': 'Original illustrated tiles generated by PayFound; no third-party artwork.',
                          'files': illustrations}}, indent=1, ensure_ascii=False))
    return counts


def curated(lst, category):
    return [{'name': n, 'key': slug(n), 'price_cents': p, 'shelf_life_hours': s, 'emoji': e, 'description': d,
             'category': category, 'fresh': True} for n, p, s, e, d in lst]


def plain(lst, category):
    return [{'name': n, 'key': slug(n), 'price_cents': p, 'emoji': e, 'description': d, 'category': category, 'fresh': False}
            for n, p, d, e in lst]


def build(off_items):
    off_pools = {k: [] for k in ('pantry', 'snack', 'frozen', 'drink')}
    for it in off_items:
        off_pools[it['pool']].append({
            'name': it['name'], 'key': it['key'], 'price_cents': it['price_cents'], 'emoji': it['emoji'],
            'description': f"{it['name']}. Packaged item; demo price and stock.",
            'category': 'Drinks' if it['pool'] == 'drink' else 'Groceries', 'fresh': False,
            'off_code': it['off_code'], 'off_category': it['off_category']})
    pools = {'produce': curated(PRODUCE, 'Fresh produce'), 'meat': curated(MEAT, 'Meat & seafood'),
             'seafood': curated(SEAFOOD, 'Meat & seafood'), 'bakery': curated(BAKERY, 'Bakery'),
             'dairy': curated(DAIRY, 'Dairy & eggs'), 'health': plain(HEALTH, 'Health & personal care'),
             'household': plain(HOUSEHOLD, 'Home & living'), **off_pools}
    menus = {}
    for kind, lst in MENUS.items():
        menus[kind] = [{**x, 'category': 'Drinks' if x['emoji'] in DRINK_EMOJI or any(w in x['name'] for w in ('Juice', 'Lassi', 'Tea'))
                        else 'Ready meals'} for x in curated(lst, 'Ready meals')]
    pools['cafe'] = menus['cafe']
    lookup = {x['name']: x for k in ('produce', 'meat', 'seafood', 'bakery', 'dairy') for x in pools[k]}

    stores_out, products_out, spot_i = [], [], 0
    for sid, sslug, name, cat, emoji, kind, hours_key, fmin, branch2, nprod, desc in STORES:
        rng = random.Random(sid)
        branches = [{'id': 'loc-' + sid, 'name': name + ' Main', 'address': SPOTS[spot_i][0] + ', San Francisco, CA',
                     'latitude': SPOTS[spot_i][1], 'longitude': SPOTS[spot_i][2]}]
        spot_i += 1
        if branch2:
            branches.append({'id': f'loc-{sid}-b2', 'name': f'{name} Second Branch', 'address': SPOTS[spot_i][0] + ', San Francisco, CA',
                             'latitude': SPOTS[spot_i][1], 'longitude': SPOTS[spot_i][2]})
            spot_i += 1
        label, days = HOURS[hours_key]
        stores_out.append({'id': sid, 'slug': sslug, 'name': name, 'category': cat, 'emoji': emoji, 'description': desc,
                           'fulfillment_minutes': fmin, 'verified': True, 'hours_label': label,
                           'hours': {str(d): [{'start': a, 'end': b} for a, b in per] for d, per in days.items()},
                           'branches': branches})

        def pool_items(pool):
            return menus[MENU_FOR[kind]] if pool == 'menu' else pools[pool]

        chosen, names = [], set()
        for m in MUST.get(kind, []):
            chosen.append(lookup[m]); names.add(m)
        for pool, count in RECIPES[kind]:
            cand = [x for x in pool_items(pool) if x['name'] not in names]
            rng.shuffle(cand)
            for x in cand[:count]:
                chosen.append(x); names.add(x['name'])
        extra = [x for pool, _ in RECIPES[kind] for x in pool_items(pool) if x['name'] not in names]
        rng.shuffle(extra)
        while len(chosen) < int(nprod * 0.96) and extra:
            x = extra.pop(); chosen.append(x); names.add(x['name'])
        chosen = chosen[:int(nprod * 0.96)]  # keeps the whole demo catalogue under the 1000-row API page used by Explore
        skew = 0.45 if hours_key in ('24h', 'long', 'cafe') else 0.35
        for i, x in enumerate(chosen, 1):
            r = rng.random()
            if r < skew:
                age = rng.randint(1, 14)          # fresh: reported < 15 minutes ago
            elif r < skew + 0.25:
                age = rng.randint(16, 60)
            elif r < skew + 0.5:
                age = rng.randint(61, 240)
            else:
                age = rng.randint(241, 720)
            qty = 0 if rng.random() < 0.03 else rng.randint(2, 40)
            branch = 1 if branch2 and rng.random() < 0.35 else 0
            p = {'id': f'g{sid[1:]}-{i:03d}', 'merchant_id': sid, 'location_id': branches[branch]['id'], 'sku': f'{sid.upper()}-{i:03d}',
                 'name': x['name'], 'key': x['key'], 'description': x['description'], 'category': x['category'],
                 'price_cents': x['price_cents'], 'quantity': qty, 'stock_age_minutes': age, 'emoji': x['emoji'],
                 'unit': unit_of(x['name']), 'fresh': bool(x['fresh'])}
            if x['fresh']:
                p['shelf_life_hours'] = x['shelf_life_hours']
            if x.get('off_code'):
                p['off_code'], p['off_category'] = x['off_code'], x['off_category']
            products_out.append(p)
    pts = [(b['latitude'], b['longitude']) for s in stores_out for b in s['branches']]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            assert metres(a, b) > 150, (a, b)
    return stores_out, products_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', type=Path, default=None, help='JSON file caching the raw Open Food Facts responses')
    ap.add_argument('--offline', action='store_true', help='use the cache only; never touch the network')
    ap.add_argument('--min-off', type=int, default=120, help='refuse to write when fewer Open Food Facts items were gathered')
    ap.add_argument('--images', action='store_true', help='download Open Food Facts front photos (CC BY-SA) and write illustrated tiles for the rest')
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()
    off = build_off(args.cache, args.offline)
    if len(off) < args.min_off:
        sys.exit(f'Only {len(off)} Open Food Facts items; refusing to write a thin catalogue')
    stores, products = build(off)
    counts = add_images(products, args.cache.parent if args.cache else Path('.')) if args.images else None
    if counts:
        print('images:', counts, file=sys.stderr)
    data = {
        'version': 1,
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'note': 'Fictional demo stores, prices, stock and freshness. Generated once by scripts/build_grocery_catalogue.py; the app never calls Open Food Facts at runtime.',
        'source': {
            'open_food_facts': {
                'name': 'Open Food Facts', 'url': 'https://world.openfoodfacts.org',
                'licence': 'Open Database Licence (ODbL) 1.0; contents under the Database Contents Licence 1.0',
                'licence_url': 'https://opendatacommons.org/licenses/odbl/1-0/',
                'attribution': 'Contains information from Open Food Facts (https://world.openfoodfacts.org), made available under the Open Database Licence (ODbL). (c) Open Food Facts contributors.',
                'used_for': 'Generic product names, categories and pack sizes of packaged groceries and drinks. Brand names removed. No images used.',
                'product_count': len(off)},
            'curated': 'Fresh produce, meat and seafood, bakery, dairy and eggs, ready meals, health and household items are fictional curated entries written for this demo.'},
        'categories': ['Groceries', 'Fresh produce', 'Meat & seafood', 'Bakery', 'Dairy & eggs', 'Ready meals', 'Drinks',
                       'Health & personal care'],
        'merchants': stores, 'products': products}
    args.out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    fresh = sum(1 for p in products if p['fresh'])
    print(f'wrote {args.out}: {len(stores)} stores, {sum(len(s["branches"]) for s in stores)} branches, {len(products)} products, {fresh} fresh')


if __name__ == '__main__':
    main()
