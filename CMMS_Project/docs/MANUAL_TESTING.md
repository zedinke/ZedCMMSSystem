# CMMS System - Manual Testing Checklist

## Overview
This document provides a comprehensive manual testing checklist for the CMMS system. All tests should be performed in both Hungarian and English languages.

---

## 1. Authentication Flow

### 1.1 Login
- [ ] Login with valid credentials (admin/admin123)
- [ ] Login with invalid username
- [ ] Login with invalid password
- [ ] Login with empty fields
- [ ] Language selector works before login
- [ ] Error messages are displayed correctly
- [ ] Error messages are localized (HU/EN)

### 1.2 Logout
- [ ] Logout button works
- [ ] User is redirected to login screen
- [ ] Session is invalidated

### 1.3 Session Expiry
- [ ] Session expires after 24 hours of inactivity
- [ ] User is prompted to login again after expiry
- [ ] Active session continues with activity

---

## 2. Asset Management

### 2.1 Production Line Management
- [ ] Create production line
- [ ] Edit production line
- [ ] Delete production line
- [ ] List all production lines
- [ ] Validation: duplicate name rejected
- [ ] All fields are localized

### 2.2 Machine Management
- [ ] Create machine
- [ ] Edit machine
- [ ] Soft delete machine (status='Selejtezve')
- [ ] Machine cannot be hard-deleted (ISO 55001 compliance)
- [ ] Machine history is tracked
- [ ] Serial number must be unique
- [ ] Machine belongs to production line
- [ ] Confirmation dialog appears before deletion
- [ ] All fields are localized

### 2.3 Module Management
- [ ] Add module to machine
- [ ] Edit module
- [ ] Delete module
- [ ] Module belongs to machine
- [ ] Confirmation dialog appears before deletion

### 2.4 Asset History
- [ ] Asset history is logged for all changes
- [ ] History shows action type, description, timestamp
- [ ] History is preserved after soft delete

---

## 3. Inventory Management

### 3.1 Part Management
- [ ] Add part with initial quantity and unit price
- [ ] Confirmation dialog shows summary before adding
- [ ] Edit part (track changes)
- [ ] Confirmation dialog shows only changed fields
- [ ] Delete part (with confirmation)
- [ ] Part cannot be deleted if has stock transactions (Szt. compliance)
- [ ] SKU must be unique
- [ ] All fields are localized

### 3.2 Stock Management
- [ ] Initial stock creates StockTransaction (audit trail)
- [ ] Stock adjustment creates StockTransaction
- [ ] Stock usage in worksheet creates StockTransaction
- [ ] All stock movements are logged (Szt. compliance)
- [ ] Stock level is updated correctly
- [ ] Low stock warning appears (red row)

### 3.3 Bulk Import
- [ ] Import parts from Excel
- [ ] Validation errors are displayed
- [ ] Rollback on error (no partial import)
- [ ] Success message shows imported count
- [ ] Error messages are localized

### 3.4 QR Code Generation
- [ ] Generate QR code for part
- [ ] QR label generation works
- [ ] File picker allows choosing download location
- [ ] QR label includes part information
- [ ] QR label uses selected template

---

## 4. Worksheet Workflow

### 4.1 Worksheet Creation
- [ ] Create worksheet
- [ ] Assign to user
- [ ] Set breakdown time
- [ ] Add description
- [ ] All fields are localized

### 4.2 Status Transitions
- [ ] Open → Waiting for Parts
- [ ] Open → Closed
- [ ] Waiting for Parts → Closed
- [ ] Invalid transitions are rejected
- [ ] Status changes are logged

### 4.3 Parts Usage
- [ ] Add part to worksheet
- [ ] Remove part from worksheet
- [ ] Stock is deducted when worksheet is closed
- [ ] Stock deduction is logged (Szt. compliance)

### 4.4 Worksheet Closure
- [ ] Mandatory fields validated (MSZ EN 13460):
  - [ ] Description required
  - [ ] Breakdown time required
  - [ ] Repair finished time required
  - [ ] Fault cause required
- [ ] Downtime is calculated correctly
- [ ] Worksheet PDF is generated
- [ ] PDF contains all mandatory fields

### 4.5 Worksheet Documents
- [ ] Generate worksheet PDF
- [ ] Download worksheet PDF
- [ ] PDF uses selected template
- [ ] All variables are replaced correctly

---

## 5. Preventive Maintenance (PM)

### 5.1 PM Task Management
- [ ] Create PM task
- [ ] Set frequency (days)
- [ ] Assign to user
- [ ] Next due date is calculated correctly
- [ ] Edit PM task
- [ ] Delete PM task (with confirmation)

### 5.2 PM Task Execution
- [ ] Execute PM task
- [ ] Complete PM task
- [ ] Task is rescheduled after completion
- [ ] Skip PM task (with reason)
- [ ] PM history is created

### 5.3 PM Dashboard
- [ ] Due today tasks are shown
- [ ] Overdue tasks are highlighted
- [ ] Upcoming tasks are listed
- [ ] Task counts are accurate

---

## 6. Vacation Management

### 6.1 Vacation Request
- [ ] Create vacation request
- [ ] Date picker works (TextField + validation)
- [ ] Workdays are calculated (excluding weekends)
- [ ] Overlapping requests are detected
- [ ] Request status is "pending"
- [ ] Confirmation dialog shows summary

### 6.2 Vacation Approval
- [ ] Manager can approve requests
- [ ] Manager can reject requests (with reason)
- [ ] User vacation days are updated on approval
- [ ] Vacation document is generated on approval
- [ ] Notification is sent to manager

### 6.3 Vacation Calendar
- [ ] Calendar view shows year
- [ ] Days are colored correctly:
  - [ ] Gray: no vacation
  - [ ] Green: approved vacation
  - [ ] Pink: pending request
- [ ] Year navigation works (previous/next)
- [ ] Day details show on click
- [ ] Legend is displayed

### 6.4 Vacation Summary
- [ ] User sees total vacation days
- [ ] User sees used vacation days
- [ ] User sees remaining vacation days
- [ ] Summary updates after approval

---

## 7. Shift Schedule

### 7.1 Shift Management
- [ ] Set shift type (single, 3-shift, 4-shift)
- [ ] Set start/end times for single shift
- [ ] Save shift schedule
- [ ] Shift schedule is displayed in table
- [ ] All fields are localized

---

## 8. Reports

### 8.1 Report Generation
- [ ] Generate worksheet report
- [ ] Generate PM report
- [ ] Generate technician report
- [ ] Apply date filters
- [ ] Apply machine filters
- [ ] Apply status filters
- [ ] Filters work correctly

### 8.2 Excel Export
- [ ] Export to Excel
- [ ] Excel contains all reports
- [ ] Excel contains charts
- [ ] Excel file opens for printing
- [ ] File picker allows choosing save location

---

## 9. Settings

### 9.1 Template Management
- [ ] Select worksheet template
- [ ] Select work request template
- [ ] Select QR label template
- [ ] Select vacation template
- [ ] Select scrapping template
- [ ] Templates are saved
- [ ] Templates are used in document generation

### 9.2 Backup & Restore
- [ ] Create backup
- [ ] Restore from backup
- [ ] Backup file is created
- [ ] Restore confirmation dialog
- [ ] Backup/restore status messages

### 9.3 Log Settings
- [ ] Set log archive years
- [ ] Set log delete years
- [ ] Settings are saved

### 9.4 Language Settings
- [ ] Switch to Hungarian
- [ ] Switch to English
- [ ] UI updates immediately
- [ ] Language preference is saved per user

---

## 10. User Management

### 10.1 User Creation
- [ ] Create user
- [ ] Set role (Manager, Technician, etc.)
- [ ] Set vacation days per year
- [ ] Set work days per week
- [ ] Password is hashed (bcrypt)
- [ ] Confirmation dialog shows summary

### 10.2 User Editing
- [ ] Edit user details
- [ ] Change role
- [ ] Update vacation days
- [ ] Confirmation dialog shows only changed fields
- [ ] Changes are logged

### 10.3 User Anonymization (GDPR)
- [ ] Anonymize user
- [ ] Confirmation dialog warns about data removal
- [ ] User data is removed (username, email, full_name)
- [ ] User statistics are preserved
- [ ] Audit trail is preserved
- [ ] Anonymization is logged

### 10.4 User Deletion
- [ ] Delete user (deprecated - should use anonymize)
- [ ] Confirmation dialog appears
- [ ] User cannot delete themselves
- [ ] Developer users cannot be deleted

---

## 11. Logs

### 11.1 Log Viewing
- [ ] View system logs
- [ ] Filter by year
- [ ] Filter by month
- [ ] Filter by category
- [ ] Search in logs
- [ ] Logs show user and timestamp
- [ ] Logs are categorized correctly

### 11.2 Log Archiving
- [ ] Old logs are archived (based on settings)
- [ ] Archived logs are accessible
- [ ] Log deletion works (based on settings)

---

## 12. Documentation

### 12.1 Template Documentation
- [ ] View worksheet template documentation
- [ ] View work request template documentation
- [ ] View QR label template documentation
- [ ] View vacation template documentation
- [ ] View scrapping template documentation
- [ ] All variables are listed
- [ ] Variable descriptions are clear
- [ ] Documentation is in both languages
- [ ] Can switch between templates

---

## 13. Bilingual Testing

### 13.1 Language Switching
- [ ] Switch language in settings
- [ ] All UI elements update immediately:
  - [ ] Menu items
  - [ ] Buttons
  - [ ] Labels
  - [ ] Error messages
  - [ ] Confirmation dialogs
  - [ ] Table headers
  - [ ] Status messages

### 13.2 Translation Completeness
- [ ] No hardcoded text in UI
- [ ] All error messages are translated
- [ ] All success messages are translated
- [ ] All confirmation dialogs are translated
- [ ] All tooltips are translated

---

## 14. Error Handling

### 14.1 Database Errors
- [ ] Database connection failure is handled
- [ ] Error message is user-friendly
- [ ] Error is logged

### 14.2 File Errors
- [ ] Invalid file upload is rejected
- [ ] File size limit is enforced
- [ ] File type validation works
- [ ] Error messages are clear

### 14.3 Validation Errors
- [ ] Required fields are validated
- [ ] Email format is validated
- [ ] SKU format is validated
- [ ] Date format is validated
- [ ] Error messages are localized

---

## 15. Performance

### 15.1 Large Datasets
- [ ] System handles 1000+ parts
- [ ] System handles 500+ worksheets
- [ ] System handles 100+ machines
- [ ] Queries complete in reasonable time (<2s)
- [ ] UI remains responsive

### 15.2 Document Generation
- [ ] PDF generation completes in <5s
- [ ] Excel export completes in <10s
- [ ] QR code generation is fast (<1s per code)

---

## 16. Compliance Testing

### 16.1 GDPR Compliance
- [ ] Passwords are hashed with bcrypt
- [ ] User anonymization works
- [ ] Audit trail is preserved after anonymization
- [ ] No PII in logs (if applicable)

### 16.2 ISO 55001 Compliance
- [ ] Assets cannot be hard-deleted
- [ ] Soft delete preserves data
- [ ] Asset history is tracked
- [ ] Full lifecycle is maintained

### 16.3 Szt. Compliance (Accounting)
- [ ] All stock movements create StockTransaction
- [ ] Audit trail is complete
- [ ] Stock adjustments are logged
- [ ] Initial stock is logged

### 16.4 MSZ EN 13460 Compliance
- [ ] Worksheet mandatory fields are validated
- [ ] PDF contains all required fields
- [ ] Dates are recorded
- [ ] Personnel are recorded

### 16.5 NAV Compliance
- [ ] No "Számla" (Invoice) term used
- [ ] Only internal documents generated
- [ ] Documents are labeled correctly

---

## 17. Known Issues / Limitations

Document any issues found during testing:

1. **Issue**: [Description]
   - **Severity**: Critical / High / Medium / Low
   - **Steps to Reproduce**: [Steps]
   - **Expected**: [Expected behavior]
   - **Actual**: [Actual behavior]

---

## 18. Test Results Summary

### Test Execution
- **Date**: [Date]
- **Tester**: [Name]
- **Environment**: [Windows 10, Python 3.12, etc.]
- **Language**: [HU/EN]

### Results
- **Total Tests**: [Number]
- **Passed**: [Number]
- **Failed**: [Number]
- **Skipped**: [Number]
- **Coverage**: [Percentage]

### Critical Issues
[List any critical issues found]

### Recommendations
[List any recommendations for improvements]

---

## Notes

- All tests should be performed in both Hungarian and English
- Test with different user roles (Manager, Technician, etc.)
- Test with various data volumes (small, medium, large)
- Document any unexpected behavior
- Take screenshots of critical issues
- Test on clean database and with existing data

