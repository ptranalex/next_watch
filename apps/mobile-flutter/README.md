# NextWatch Mobile App

A Flutter-based mobile application for the NextWatch platform.

## Features

- Cross-platform mobile app (iOS and Android)
- Native movie browsing experience
- User authentication and profiles
- Personal watchlist management
- Movie tracking (watched, liked)
- Offline support for watchlist data
- Push notifications for new releases

## Setup

### Prerequisites

- Flutter SDK 3.10+
- Dart 3.0+
- Android Studio or Xcode for native development
- Firebase project (for authentication and push notifications)

### Installation

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

### Running the App

```bash
# Run in debug mode
flutter run

# Run with specific device
flutter run -d <device_id>

# For iOS simulator
flutter run -d ios

# For Android emulator
flutter run -d android
```

## Architecture

The app follows a clean architecture pattern with the following layers:

- **Presentation**: UI components, screens, and widgets
- **Application**: Use cases and application logic
- **Domain**: Business logic and entities
- **Infrastructure**: Data sources, repositories, and external services

### Directory Structure

```
mobile-flutter/
├── lib/
│   ├── app/              # App configuration and initialization
│   ├── config/           # Environment configuration
│   ├── features/         # Feature modules
│   │   ├── auth/         # Authentication feature
│   │   ├── movies/       # Movie browsing and details
│   │   ├── profile/      # User profile management
│   │   └── watchlist/    # Watchlist management
│   ├── core/             # Core utilities and shared components
│   ├── navigation/       # Routing and navigation
│   ├── services/         # External services (API, local storage)
│   └── main.dart         # Entry point
├── test/                 # Test files
├── pubspec.yaml          # Dependencies
└── README.md             # This file
```

## Development

### State Management

The app uses [provider/riverpod/bloc] for state management with the following principles:

- Separation of UI and business logic
- Reactive programming with streams
- Dependency injection for testability

### API Integration

The app connects to the NextWatch backend API using:

- REST client for main API communication
- WebSockets for real-time updates (future)
- Secure token storage for authentication

### Testing

```bash
# Run all tests
flutter test

# Run specific test file
flutter test test/features/movies/movie_service_test.dart
```

## Deployment

### Android

```bash
# Build APK
flutter build apk --release

# Build App Bundle for Play Store
flutter build appbundle --release
```

### iOS

```bash
# Build for iOS
flutter build ios --release

# Then use Xcode to archive and upload to App Store
```

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
