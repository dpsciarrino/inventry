# Inventry
A light-weight parts inventory and BOM management tool utilizing Python and a SQLite database.

## Version Notes

### v0.1
**Current Features:**
- Add/Edit/View parts (manufacturer, manufacturer part number, and tiered pricing)
- Add/Edit/View bill of materials.
- Calculate total cost of a single BOM using tiered pricing.
- Calculate total cost of building multiple quantities of one BOM.

**Future Upgrades:**
- Field validation on all applets (required)
- Smoother UI experience
- Encapsulated tkinter components, as opposed to standard out-of-the-box.
- Support for vendor/part association.
- Support for web scraping tiered pricing data from major distributors (Mouser, DigiKey, etc.)
