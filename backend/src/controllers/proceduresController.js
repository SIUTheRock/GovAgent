/* ---------------------------------------------------------
 * Copyright (c) 2025 PPNCKH Contributors
 * Licensed under the MIT License.
 * --------------------------------------------------------- */
const pool = require('../db/postgres');
const axios = require('axios');

// Tích hợp OpenStreetMap lấy tọa độ (FiWARE IoT/Location)
async function getCoordinatesFromOSM(agencyName) {
  try {
    if (!agencyName) return { lat: 10.7769, lon: 106.7009 };
    const query = encodeURIComponent(agencyName + ', Việt Nam');
    const response = await axios.get(`https://nominatim.openstreetmap.org/search?q=${query}&format=json&limit=1`, {
      headers: { 'User-Agent': 'PPNCKH-SmartCityPlatform-OLP2025' }
    });
    if (response.data && response.data.length > 0) {
      return {
        lat: parseFloat(response.data[0].lat),
        lon: parseFloat(response.data[0].lon)
      };
    }
  } catch (error) {
    console.error("OSM Error:", error.message);
  }
  return { lat: 10.7769, lon: 106.7009 }; // Mặc định HCM
}

// GET /api/procedures?page=1&limit=12&category=&level=
async function getProcedures(req, res) {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(50, Math.max(1, parseInt(req.query.limit) || 12));
    const offset = (page - 1) * limit;
    const categoryId = req.query.category ? parseInt(req.query.category) : null;
    const level = req.query.level || null;

    const conditions = ['p.is_active = TRUE'];
    const params = [];

    if (categoryId) {
      params.push(categoryId);
      conditions.push(`p.category_id = $${params.length}`);
    }
    if (level) {
      params.push(level);
      conditions.push(`p.level = $${params.length}`);
    }

    const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

    const countResult = await pool.query(
      `SELECT COUNT(*) FROM procedures p ${where}`,
      params
    );
    const total = parseInt(countResult.rows[0].count);

    params.push(limit);
    params.push(offset);
    const dataResult = await pool.query(
      `SELECT p.id, p.code, p.name, p.level, p.implementing_agency,
              p.processing_time, p.fee, c.name AS category_name, c.slug AS category_slug
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       ${where}
       ORDER BY p.name ASC
       LIMIT $${params.length - 1} OFFSET $${params.length}`,
      params
    );

    res.json({
      data: dataResult.rows,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy danh sách thủ tục' });
  }
}

// GET /api/procedures/:id
async function getProcedureById(req, res) {
  try {
    const id = parseInt(req.params.id);
    const format = req.query.format;
    if (!id || id < 1) return res.status(400).json({ error: 'ID không hợp lệ.' });

    const result = await pool.query(
      `SELECT p.*, c.name AS category_name, c.slug AS category_slug
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       WHERE p.id = $1 AND p.is_active = TRUE`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Không tìm thấy thủ tục.' });
    }
    const procedure = result.rows[0];

    // Tăng view count
    pool.query('UPDATE procedures SET view_count = view_count + 1 WHERE id = $1', [id]);

    // Trả về định dạng NGSI-LD (ETSI / FIWARE Smart Data Models)
    if (format === 'ngsi-ld') {
      const geo = await getCoordinatesFromOSM(procedure.implementing_agency);
      const ngsiLd = {
        "@context": [
          "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
          "https://smartdatamodels.org/context.jsonld"
        ],
        "id": `urn:ngsi-ld:PublicService:${procedure.code}`,
        "type": "PublicService",
        "name": { "type": "Property", "value": procedure.name },
        "description": { "type": "Property", "value": procedure.description || `Thủ tục ${procedure.name}` },
        "serviceProvider": { "type": "Property", "value": procedure.implementing_agency || "Cơ quan hành chính nhà nước" },
        "location": {
          "type": "GeoProperty",
          "value": { "type": "Point", "coordinates": [geo.lon, geo.lat] }
        }
      };
      res.setHeader('Content-Type', 'application/ld+json');
      return res.json(ngsiLd);
    }

    res.json({ data: procedure });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy chi tiết thủ tục.' });
  }
}

// GET /api/procedures/:id/json-ld (JSON-LD schema.org cơ bản)
async function getProcedureJsonLd(req, res) {
  try {
    const id = parseInt(req.params.id);
    if (!id || id < 1) return res.status(400).json({ error: 'ID không hợp lệ.' });

    const result = await pool.query(
      `SELECT p.*, c.name AS category_name
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       WHERE p.id = $1 AND p.is_active = TRUE`,
      [id]
    );

    if (result.rows.length === 0) return res.status(404).json({ error: 'Không tìm thấy thủ tục.' });
    const procedure = result.rows[0];
    
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "PublicService",
      "identifier": procedure.code,
      "name": procedure.name,
      "provider": {
        "@type": "GovernmentOrganization",
        "name": procedure.implementing_agency || "Cơ quan hành chính nhà nước"
      },
      "serviceType": procedure.category_name
    };

    res.setHeader('Content-Type', 'application/ld+json');
    res.json(jsonLd);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy dữ liệu JSON-LD.' });
  }
}

module.exports = { getProcedures, getProcedureById, getProcedureJsonLd };