# Changelog

All notable changes to the CMMS system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-14

### Added
- Complete CMMS system with modern FastAPI-inspired UI design
- Asset Management: Production lines, machines, modules with full lifecycle tracking
- Inventory Management: Parts, suppliers, stock transactions with audit trail (Szt. compliance)
- Worksheet Management: Complete workflow from creation to closure with MSZ EN 13460 compliance
- Preventive Maintenance: PM tasks with scheduling and execution tracking
- Vacation Management: Request, approval workflow, calendar view, document generation
- Shift Schedule Management: User shift patterns (single, 3-shift, 4-shift)
- Reports: Comprehensive reporting with Excel export and charts
- User Management: Role-based access control, GDPR-compliant anonymization
- Logging System: Comprehensive system logs with archiving and deletion policies
- Scrapping Documents: Automatic generation for scrapped parts/assets and materials
- Template System: Configurable DOCX templates for worksheets, work requests, QR labels, vacation, scrapping
- Bilingual Support: Full Hungarian and English localization
- Compliance Features:
  - GDPR: Password hashing (bcrypt), user anonymization, audit trail preservation
  - ISO 55001: Soft delete for assets, full lifecycle tracking
  - Szt. (2000. évi C. törvény): Complete audit trail for all inventory movements
  - MSZ EN 13460: Mandatory fields validation for worksheets
  - NAV Compliance: Internal documents only, no invoice terminology

### Security
- Bcrypt password hashing (GDPR compliance)
- SQL injection prevention (parameterized queries)
- File upload validation (type, size, MIME)
- Session management with expiry
- Role-based access control
- Comprehensive audit logging

### Testing
- Unit tests for models, services, and utilities
- Integration tests for complete workflows
- Security tests (SQL injection, file upload, authorization)
- Performance tests (database queries, PDF generation, Excel export)
- Manual testing checklist

### Documentation
- User Manual
- Installation Guide
- Technical Documentation
- Template Documentation
- API Documentation
- Compliance Status Documentation

---

## [Unreleased]

### Planned
- Performance optimizations based on test results
- Additional language support
- Mobile app (Android)
- Advanced reporting features
- Integration with external systems

