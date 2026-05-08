const express = require('express');
const router = express.Router();
const { getProcedures, getProcedureById, getProcedureJsonLd } = require('../controllers/proceduresController');

router.get('/', getProcedures);
router.get('/:id', getProcedureById);
router.get('/:id/json-ld', getProcedureJsonLd); // Route LOD trả về JSON-LD API

module.exports = router;
