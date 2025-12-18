# Release Checklist

This checklist must be completed before each release of the CMMS system.

## Pre-Release Testing

### Unit Tests
- [ ] All unit tests pass (`pytest tests/test_models.py -v`)
- [ ] All unit tests pass (`pytest tests/test_services.py -v`)
- [ ] All unit tests pass (`pytest tests/test_utils.py -v`)
- [ ] Test coverage is at least 70% for services
- [ ] Test coverage is at least 80% for models
- [ ] Test coverage is at least 80% for utilities

### Integration Tests
- [ ] All integration tests pass (`pytest tests/test_integration.py -v`)
- [ ] Worksheet workflow test passes
- [ ] PM task workflow test passes
- [ ] Vacation request workflow test passes
- [ ] Inventory import workflow test passes

### Security Tests
- [ ] All security tests pass (`pytest tests/test_security.py -v`)
- [ ] SQL injection prevention verified
- [ ] File upload validation verified
- [ ] Password hashing (bcrypt) verified
- [ ] Authorization checks verified
- [ ] Audit logging verified

### Performance Tests
- [ ] All performance tests pass (`pytest tests/test_performance.py -v`)
- [ ] Database queries complete in <2s for 1000+ records
- [ ] PDF generation completes in <5s
- [ ] Excel export completes in <10s
- [ ] Memory usage is acceptable

### Manual Testing
- [ ] Manual testing checklist completed (see `docs/MANUAL_TESTING.md`)
- [ ] All critical workflows tested
- [ ] Both languages (HU/EN) tested
- [ ] All user roles tested
- [ ] No critical bugs found

---

## Code Quality

### Code Review
- [ ] No debug code or print statements (except logging)
- [ ] No commented-out code blocks
- [ ] No TODO comments in production code
- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings

### Linting
- [ ] No linter errors (`pylint` or similar)
- [ ] No type checking errors (if using mypy)
- [ ] All imports are used
- [ ] No unused variables

---

## Documentation

### User Documentation
- [ ] `USER_MANUAL.md` is up-to-date
- [ ] All new features documented
- [ ] Screenshots updated (if applicable)
- [ ] FAQ section updated
- [ ] Troubleshooting section updated

### Technical Documentation
- [ ] `TECHNICAL.md` is up-to-date
- [ ] Architecture documented
- [ ] API documentation updated (if applicable)
- [ ] Database schema documented
- [ ] Deployment guide updated

### Installation Documentation
- [ ] `INSTALLATION.md` is up-to-date
- [ ] System requirements listed
- [ ] Installation steps verified
- [ ] Troubleshooting for common issues
- [ ] Update instructions included

### Template Documentation
- [ ] All templates documented in `documentation_screen.py`
- [ ] All variables listed with descriptions
- [ ] Usage instructions provided (HU/EN)
- [ ] Format descriptions provided

---

## Version Management

### Version Information
- [ ] `version.txt` updated with new version number
- [ ] `CHANGELOG.md` updated with all changes
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] `app_config.py` reads version from `version.txt`

### About Dialog
- [ ] About dialog shows correct version
- [ ] About dialog shows compliance information
- [ ] About dialog is localized (HU/EN)

---

## Localization

### Translation Completeness
- [ ] All UI strings are localized
- [ ] No hardcoded text in UI
- [ ] All error messages are localized
- [ ] All success messages are localized
- [ ] Translation completeness check passes
- [ ] Both `hu.json` and `en.json` have all keys

### Translation Quality
- [ ] Hungarian translations are grammatically correct
- [ ] English translations are grammatically correct
- [ ] Technical terms are consistent
- [ ] No placeholder text visible to users

---

## Compliance

### GDPR & Infotv. (Data Privacy)
- [ ] Passwords are hashed with bcrypt (not plaintext)
- [ ] User anonymization works correctly
- [ ] Audit trail is preserved after anonymization
- [ ] No PII in logs (if applicable)
- [ ] Right to be Forgotten implemented

### ISO 55001 (Asset Management)
- [ ] Assets cannot be hard-deleted
- [ ] Soft delete preserves data (status='Selejtezve')
- [ ] Asset history is tracked
- [ ] Full lifecycle is maintained

### 2000. évi C. törvény (Szt. - Accounting)
- [ ] All stock movements create StockTransaction
- [ ] Audit trail is complete
- [ ] Stock adjustments are logged
- [ ] Initial stock is logged

### MSZ EN 13460 (Maintenance Docs)
- [ ] Worksheet mandatory fields are validated:
  - [ ] Description required
  - [ ] Breakdown time required
  - [ ] Repair finished time required
  - [ ] Fault cause required
- [ ] PDF contains all required fields
- [ ] Dates are recorded
- [ ] Personnel are recorded

### NAV Compliance
- [ ] No "Számla" (Invoice) term used
- [ ] Only internal documents generated
- [ ] Documents are labeled correctly

---

## Build & Deployment

### Executable Build
- [ ] `build.spec` is up-to-date
- [ ] All data files included (translations, templates, icons)
- [ ] All hidden imports specified
- [ ] Icon file path is correct
- [ ] Executable builds successfully (`python build.py`)
- [ ] Executable tested on clean Windows machine
- [ ] No missing dependencies

### Installer (Optional)
- [ ] Installer created (NSIS or Inno Setup)
- [ ] Uninstaller works correctly
- [ ] Start menu shortcuts created
- [ ] Desktop shortcut option works
- [ ] Installation tested

### Backup/Restore
- [ ] Backup functionality tested
- [ ] Restore functionality tested
- [ ] Scheduled backups work correctly
- [ ] Backup retention policy works
- [ ] Backup validation works

---

## Performance

### Query Optimization
- [ ] No N+1 query issues
- [ ] Indexes are used correctly
- [ ] Slow queries optimized
- [ ] Database performance acceptable

### Memory Management
- [ ] No memory leaks detected
- [ ] Memory usage is acceptable
- [ ] Large datasets handled efficiently

### File Operations
- [ ] PDF generation is optimized
- [ ] Excel export is optimized
- [ ] Progress indicators for long operations
- [ ] File operations complete in reasonable time

---

## Security Audit

### Password Security
- [ ] Bcrypt is used (not Argon2 - per compliance requirement)
- [ ] Password strength requirements enforced
- [ ] Password change functionality works

### Data Privacy (GDPR)
- [ ] User anonymization preserves audit trail
- [ ] "Right to be Forgotten" functionality works
- [ ] PII removal works correctly

### File Security
- [ ] File upload validation works
- [ ] File type restrictions enforced
- [ ] File size limits enforced

### Session Security
- [ ] Session expiry works
- [ ] Session token generation is secure
- [ ] Concurrent session handling works

### SQL Injection
- [ ] All queries use parameterized statements
- [ ] No raw SQL with user input
- [ ] Tested with malicious input

### Authorization
- [ ] Role-based access control works
- [ ] Unauthorized access attempts are blocked
- [ ] Permission checks in all services

---

## Known Issues

### Documented Issues
- [ ] All known issues documented
- [ ] Workarounds provided (if applicable)
- [ ] Priority assigned to issues
- [ ] Timeline for fixes provided (if applicable)

### Limitations
- [ ] System limitations documented
- [ ] Feature limitations documented
- [ ] Performance limitations documented

---

## Final Checks

### Pre-Release
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] README.md updated
- [ ] No critical bugs
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] Compliance verified

### Release
- [ ] Release notes prepared
- [ ] Release tagged in version control
- [ ] Executable packaged
- [ ] Installer created (if applicable)
- [ ] Release announcement prepared

---

## Post-Release

### Monitoring
- [ ] Error logs monitored
- [ ] User feedback collected
- [ ] Performance metrics tracked
- [ ] Security issues monitored

### Support
- [ ] Support documentation ready
- [ ] Known issues tracked
- [ ] Bug reports process in place
- [ ] Update process documented

---

## Checklist Completion

**Release Version**: _______________

**Release Date**: _______________

**Completed By**: _______________

**Sign-off**: _______________

---

## Notes

Additional notes or comments:

_________________________________________________________
_________________________________________________________
_________________________________________________________

