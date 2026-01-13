# Floor Finder Feature

## Overview

The Floor Finder feature allows users to search for locations across all floors without needing to know which floor a location is on. This is an **additive feature** that doesn't modify any existing navigation logic.

## How It Works

### User Interface

Two new "🔍 All Floors" buttons have been added:
- One next to the **Start** search input
- One next to the **Destination** search input

### Usage

1. **Click the "🔍 All Floors" button** next to either search input
2. The button will highlight in gold to indicate cross-floor search is active
3. **Type your search query** (e.g., "Physics Lab", "Reception", "Room 101")
4. **Results from all floors** will be displayed, with the floor prominently shown
5. **Click on a result** to:
   - Select that location
   - Automatically switch to the correct floor
   - Exit cross-floor search mode

### Example Scenarios

#### Scenario 1: Finding a Room Without Knowing the Floor
```
User: "I need to go to the Physics Lab but don't know what floor it's on"
1. Click "🔍 All Floors" button
2. Type "Physics Lab"
3. See results showing:
   - Physics Lab FF1 (Front) - First Floor
   - Physics Lab FF2 (Front) - First Floor
   - Physics Lab FF1 (Back) - First Floor
4. Click the desired lab
5. Map automatically switches to First Floor
```

#### Scenario 2: Finding a Person's Office
```
User: "Where is the Principal's Office?"
1. Click "🔍 All Floors" button
2. Type "Principal"
3. See results showing:
   - Principal's Office - Ground Floor
   - Principal's Secretary's Office - Ground Floor
4. Click to select and navigate
```

## Technical Details

### Files Added
- **`floor-finder.js`**: Contains all the floor finder logic

### Files Modified
- **`index.html`**: Added script tag to load `floor-finder.js`
- **`main.js`**: Added initialization call for the floor finder feature

### Key Functions

#### `searchAcrossAllFloors(query)`
Searches through all nodes regardless of floor, excluding corridors.

**Parameters:**
- `query` (string): The search term

**Returns:**
- Array of matching nodes, sorted by relevance and floor order

#### `renderCrossFloorResults(role, results)`
Displays search results with floor information prominently highlighted.

**Parameters:**
- `role` (string): Either 'start' or 'end'
- `results` (Array): Array of node objects to display

#### `toggleFloorFinder(role)`
Toggles the cross-floor search mode on/off.

**Parameters:**
- `role` (string): Either 'start' or 'end'

#### `initFloorFinder()`
Initializes the floor finder feature by adding UI buttons and event listeners.

### Design Principles

1. **Non-Invasive**: The feature is completely additive and doesn't modify existing routing or search logic
2. **User-Friendly**: Clear visual feedback when cross-floor search is active
3. **Automatic Floor Switching**: Selecting a result automatically switches to the correct floor
4. **Smart Filtering**: Excludes corridors from cross-floor search to show only meaningful locations

## Styling

The feature uses existing Tailwind CSS classes and custom styles:

- **Active State**: Gold background (`bg-gold`) with white text
- **Inactive State**: Border with slate text
- **Results**: Same styling as existing search results, with floor information emphasized

## Browser Compatibility

Works in all modern browsers that support:
- ES6 JavaScript
- DOM manipulation
- CSS transforms

## Future Enhancements

Potential improvements:
1. Add keyboard shortcuts (e.g., Ctrl+F for cross-floor search)
2. Show distance/floor difference in results
3. Add "Recently searched" locations
4. Implement fuzzy search for better matching
5. Add voice search capability

## Maintenance

The feature is self-contained in `floor-finder.js`. To disable it:
1. Remove the `<script src="floor-finder.js"></script>` line from `index.html`
2. Remove the `initFloorFinder()` call from `main.js`

No other changes needed!
