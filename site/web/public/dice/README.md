# Dice SVG Assets

Place one SVG file per die in web/public/dice/ for the DiceDisplay component:

- `d4.svg`
- `d6.svg`
- `d8.svg`
- `d10.svg`
- `d12.svg`
- `d20.svg`
- `d100.svg`

Draw each SVG as an outline-style die with a transparent center that holds the roll result number.

If an SVG file is missing, the DiceDisplay component falls back to a CSS-rendered die shape with the die type label and the roll result.
