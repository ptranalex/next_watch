***REMOVED*** NextWatch Mobile App

A Flutter-based mobile application for the NextWatch platform.

***REMOVED******REMOVED*** Features

- Cross-platform mobile app (iOS and Android)
- Native movie browsing experience
- User authentication and profiles
- Personal watchlist management
- Movie tracking (watched, liked)
- Offline support for watchlist data
- Push notifications for new releases

***REMOVED******REMOVED*** Setup

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Flutter SDK 3.10+
- Dart 3.0+
- Android Studio or Xcode for native development
- Firebase project (for authentication and push notifications)

***REMOVED******REMOVED******REMOVED*** Installation

1. Install Flutter by following the [official installation guide](https://flutter.dev/docs/get-started/install)
2. Clone the repository
3. Install dependencies:

```bash
cd apps/mobile-flutter
flutter pub get
```

4. Configure environment:
   - Copy `lib/config/.env.example` to `lib/config/.env`
   - Update API endpoint and other environment variables

***REMOVED******REMOVED******REMOVED*** Running the App

```bash
***REMOVED*** Run in debug mode
flutter run

***REMOVED*** Run with specific device
flutter run -d <device_id>

***REMOVED*** For iOS simulator
flutter run -d ios

***REMOVED*** For Android emulator
flutter run -d android
```

***REMOVED******REMOVED*** Architecture

The app follows a clean architecture pattern with the following layers:

- **Presentation**: UI components, screens, and widgets
- **Application**: Use cases and application logic
- **Domain**: Business logic and entities
- **Infrastructure**: Data sources, repositories, and external services

***REMOVED******REMOVED******REMOVED*** Directory Structure

```
mobile-flutter/
├── lib/
│   ├── app/              ***REMOVED*** App configuration and initialization
│   ├── config/           ***REMOVED*** Environment configuration
│   ├── features/         ***REMOVED*** Feature modules
│   │   ├── auth/         ***REMOVED*** Authentication feature
│   │   ├── movies/       ***REMOVED*** Movie browsing and details
│   │   ├── profile/      ***REMOVED*** User profile management
│   │   └── watchlist/    ***REMOVED*** Watchlist management
│   ├── core/             ***REMOVED*** Core utilities and shared components
│   ├── navigation/       ***REMOVED*** Routing and navigation
│   ├── services/         ***REMOVED*** External services (API, local storage)
│   └── main.dart         ***REMOVED*** Entry point
├── test/                 ***REMOVED*** Test files
├── pubspec.yaml          ***REMOVED*** Dependencies
└── README.md             ***REMOVED*** This file
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** State Management

The app uses [provider/riverpod/bloc] for state management with the following principles:

- Separation of UI and business logic
- Reactive programming with streams
- Dependency injection for testability

***REMOVED******REMOVED******REMOVED*** API Integration

The app connects to the NextWatch backend API using:

- REST client for main API communication
- WebSockets for real-time updates (future)
- Secure token storage for authentication

***REMOVED******REMOVED******REMOVED*** Testing

```bash
***REMOVED*** Run all tests
flutter test

***REMOVED*** Run specific test file
flutter test test/features/movies/movie_service_test.dart
```

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Android

```bash
***REMOVED*** Build APK
flutter build apk --release

***REMOVED*** Build App Bundle for Play Store
flutter build appbundle --release
```

***REMOVED******REMOVED******REMOVED*** iOS

```bash
***REMOVED*** Build for iOS
flutter build ios --release

***REMOVED*** Then use Xcode to archive and upload to App Store
```

***REMOVED******REMOVED*** Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
