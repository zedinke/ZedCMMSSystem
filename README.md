# CMMS - Computerized Maintenance Management System

**Professional bilingual (English/Hungarian) desktop maintenance management application built with Python and Flet.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 📋 Rendszer Áttekintés / System Overview

A CMMS (Computerized Maintenance Management System) egy átfogó karbantartáskezelő rendszer, amely segít a gépek, berendezések, készletek és munkafolyamatok hatékony kezelésében.

The CMMS (Computerized Maintenance Management System) is a comprehensive maintenance management system that helps efficiently manage machines, equipment, inventory, and workflows.

### Főbb Jellemzők / Key Features

- ✅ **Kétnyelvű támogatás / Bilingual Support**: Magyar és Angol felhasználói felület
- ✅ **Szerepkör alapú hozzáférés / Role-based Access**: Adminisztrátor, Műszakvezető, Karbantartó, Termelő
- ✅ **Valós idejű értesítések / Real-time Notifications**: PM feladatok, munkalapok állapotváltozásai
- ✅ **SQLite adatbázis / SQLite Database**: Egyszerű telepítés és karbantartás
- ✅ **Teljes dokumentáció / Complete Documentation**: Részletes rendszer dokumentáció letölthető DOCX formátumban

---

## 🚀 Gyors Indítás / Quick Start

### Desktop Alkalmazás / Desktop Application

```bash
cd CMMS_Project
python main.py
```

### Telepítés / Installation

Lásd: [CMMS_Project/README.md](CMMS_Project/README.md) - Részletes telepítési útmutató

---

## 📁 Projekt Struktúra / Project Structure

```
ZedCMMSSystem/
├── CMMS_Project/        # Desktop alkalmazás (Python + Flet)
│   ├── README.md        # Részletes dokumentáció
│   ├── main.py          # Fő alkalmazás
│   ├── services/        # 43 szolgáltatás modul
│   ├── ui/              # 22 UI képernyő
│   └── docs/            # 47+ dokumentáció fájl
│
├── AndroidApp/          # Android alkalmazás (Kotlin + Jetpack Compose)
│   └── README.md        # Android app dokumentáció
│
└── docs/                # Projekt szintű dokumentáció
```

---

## 🎯 Főbb Funkciók / Main Features

### Desktop Alkalmazás

1. **Eszközkezelés / Asset Management**
   - Production Line (Termelési sorok)
   - Assets (Gépek, berendezések)
   - Parts (Alkatrészek)

2. **Karbantartáskezelés / Maintenance Management**
   - PM (Preventive Maintenance)
   - Worksheets (Munkalapok)
   - Service Records (Szerviz feljegyzések)

3. **Készletkezelés / Inventory Management**
   - Storage (Raktározás)
   - Inventory Audit (Készletellenőrzés)

4. **Jelentések / Reports**
   - PDF és CSV export
   - Statisztikák és grafikonok

### Android Alkalmazás

- Offline-first architektúra
- Teljes CRUD műveletek
- Valós idejű szinkronizáció
- Material Design 3 UI

---

## 📚 Dokumentáció / Documentation

- **[CMMS_Project/README.md](CMMS_Project/README.md)** - Teljes rendszer dokumentáció
- **[AndroidApp/README.md](AndroidApp/README.md)** - Android app dokumentáció
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Gyors indítási útmutató

---

## 🛠️ Technológiai Stack / Technology Stack

### Desktop
- **Python 3.9+**
- **Flet** - Cross-platform UI framework
- **SQLite** - Adatbázis
- **FastAPI** - REST API
- **SQLAlchemy** - ORM

### Android
- **Kotlin**
- **Jetpack Compose** - Modern UI
- **Room** - Lokális adatbázis
- **Retrofit** - API integráció
- **Material Design 3**

---

## 📊 Statisztikák / Statistics

- **~50,000+** sor Python kód
- **43** Service modul
- **22** UI képernyő
- **86** Adatbázis tábla
- **2** Lokalizáció (Magyar, Angol)
- **47+** Dokumentáció fájl

---

## 🔐 Biztonság / Security

- Argon2 jelszó hashelés
- Token alapú autentikáció
- Szerepkör alapú hozzáférés-vezérlés
- Audit log minden műveletre

---

## 📝 Licenc / License

Proprietary - All rights reserved

---

## 👥 Fejlesztők / Developers

Artence Development Team

---

**Verzió / Version**: 1.0.0  
**Legutóbbi frissítés / Last Update**: 2025.12.18

---

*Az alkalmazás folyamatosan fejlesztés alatt áll. Minden javaslat és visszajelzés szívesen várható.*

*The application is under continuous development. All suggestions and feedback are welcome.*

