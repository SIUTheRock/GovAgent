const express = require('express');
const router = express.Router();
const { getProcedures, getProcedureById } = require('../controllers/proceduresController');

router.get('/', getProcedures);
router.get('/:id', getProcedureById);

module.exports = router;
