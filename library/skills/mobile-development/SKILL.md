---
name: mobile-development
description: Cross-platform and native mobile development patterns including React Native, responsive design, and app architecture
---

# Mobile Development

## React Native
- Core components: View, Text, ScrollView, FlatList, TouchableOpacity, Pressable
- Styling: StyleSheet.create, flexbox layout (default flex direction: column)
- Navigation: React Navigation — Stack, Tab, Drawer navigators
- State: same React hooks (useState, useContext), Redux, Zustand
- Platform-specific: Platform.OS, Platform.select, .ios.js/.android.js files
- Native modules: bridging native APIs to JavaScript
- Expo: managed workflow, EAS Build, expo-router (file-based routing)
- Animations: Animated API, Reanimated 2 (worklets, shared values)
- Lists: FlatList with keyExtractor, renderItem, getItemLayout for perf
- Async storage: @react-native-async-storage for persistence
- Networking: fetch API, same as web React
- New Architecture: Fabric renderer, TurboModules, JSI (JavaScript Interface)

## App Architecture Patterns
- MVVM: Model-View-ViewModel for clean separation
- Clean Architecture: domain, data, presentation layers
- Repository pattern: abstract data access behind interfaces
- Offline-first: local DB (SQLite, Realm) + sync layer
- State machines: finite states for screen flows, auth states

## Responsive and Adaptive Design
- Dimensions API: Dimensions.get('window')
- useWindowDimensions hook for reactive sizing
- Flexbox: flex, justifyContent, alignItems, flexWrap
- Percentage-based sizing with flex ratios
- Safe areas: SafeAreaView, useSafeAreaInsets
- Breakpoints: phone, tablet, desktop-like layouts

## Performance
- FlatList over ScrollView for long lists
- memo, useMemo, useCallback to prevent re-renders
- Image optimization: resize, cache, FastImage library
- Bundle size: code splitting, lazy loading
- Hermes engine: faster startup, reduced memory (default in React Native)
- Flipper/React DevTools for debugging performance

## Native APIs
- Camera: expo-camera, react-native-camera
- Location: expo-location, Geolocation API
- Push notifications: Firebase Cloud Messaging, expo-notifications
- File system: expo-file-system, react-native-fs
- Biometrics: expo-local-authentication, touch/face ID
- Deep linking: URL schemes, universal/app links

## App Store Deployment
- iOS: App Store Connect, Xcode, provisioning profiles, certificates
- Android: Google Play Console, signing keys, AAB format
- Code signing: important for both platforms
- Beta testing: TestFlight (iOS), Internal Testing (Android)
- OTA updates: CodePush, EAS Update for non-native changes
- CI/CD: Fastlane, EAS Build, GitHub Actions

## Testing
- Jest for unit tests
- React Native Testing Library: render, screen, fireEvent
- Detox: E2E testing for React Native
- Manual testing: simulators/emulators + real devices
- Accessibility: accessibilityLabel, accessibilityRole, screen reader testing

## Best Practices
- Test on real devices — simulators miss real-world issues
- Handle offline state gracefully — mobile networks are unreliable
- Respect platform conventions: back button (Android), swipe back (iOS)
- Keep bundle size small — users download over cellular
- Use environment configs for different build variants
- Implement crash reporting: Sentry, Crashlytics
- Plan for multiple screen sizes from the start
