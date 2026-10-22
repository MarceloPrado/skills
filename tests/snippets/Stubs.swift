import SwiftUI

struct Workout: Identifiable { let id: UUID; let name: String }
struct Item: Identifiable { let id: Int }
struct WorkoutList: View { var body: some View { EmptyView() } }
struct WorkoutDetail: View { let id: Workout.ID; var body: some View { EmptyView() } }
struct ProfileButton: View { var body: some View { EmptyView() } }
struct ExerciseVideo: View { var body: some View { EmptyView() } }
struct SetLog: View { var body: some View { EmptyView() } }
struct SetControls: View { var body: some View { EmptyView() } }
struct SetRows: View { var body: some View { EmptyView() } }
struct RestControls: View { var body: some View { EmptyView() } }
struct Row: View { let item: Item; var body: some View { EmptyView() } }
struct CameraScreen: View { var body: some View { EmptyView() } }
struct Teleprompter: View { var body: some View { EmptyView() } }
