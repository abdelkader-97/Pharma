# Odoo Module: dw_quality


## Overview

The dw_quality module is a combination between the two original Odoo modules "quality" and "quality_control", it is totally refactored, any relation to the emails from the original modules have been removed, the relation to the module mrp has been removed, the reporting menu has been removed, the views (graph, pivot, kanban and activity) has been removed along with all the actions and variables related to them. It includes all the features of the original module, along with additional functionalities such as quality alerts, quality checks, and quality control points.
This module is meant to be used as a temporary solution the time a fully customized quality module is developed.
#### Version of th module: 1.0
#### Version of th Odoo: 18

---

## Installation

 
---

##  Features
- Quality Alerts: Create and manage quality alerts to track and address quality issues.
- Quality Checks: Define and perform quality checks to ensure products meet specified standards.
- Quality Control Points: Set up quality control points in the production process to monitor and maintain quality.
- Integration with Inventory: Seamlessly integrate quality management with inventory operations.

---

##  Menus
- Quality Control/Control Points
- Quality Control/Quality Checks
- Quality Control/Quality Alerts
- Products/Products
- Products/Product Variants
- Products/Lots serial numbers
- Configuration/Quality Teams
- Configuration/Quality Alert Stages
- Configuration/Quality Tags

---

## Groups added
 
---

## Dependencies
stock

---

##  Client for which it has been developed

---

## Tests (if applies)

- test_quality_picking.py
- test_quality_alert.py
- test_quality_stock_lot.py
- test_quality_products.py
- test_quality_alert_team.py
- test_quality_point.py
- test_quality_check.py


---

##  Possible Optimizations

---

##  Credit

---

## License

---

---
---
## Any addition/improvement after the official deployment of the product

---
