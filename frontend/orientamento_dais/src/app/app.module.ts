import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgCeilPipeModule } from 'angular-pipes';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { UserLoginComponent } from './user-login/user-login.component';
import { StudentSignupComponent } from './student-signup/student-signup.component';

import { UserHttpService } from './user-http.service';
import { ActivateProfileComponent } from './activate-profile/activate-profile.component';
import { HomeComponent } from './home/home.component';
import { TopBarComponent } from './top-bar/top-bar.component';
import { CourseCardComponent } from './course-card/course-card.component';
import { CarouselComponent } from './carousel/carousel.component';
import { CarouselItemComponent } from './carousel-item/carousel-item.component';
import { CoursesComponent } from './courses/courses.component';
import { CourseDetailComponent } from './course-detail/course-detail.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatTabsModule } from '@angular/material/tabs';
import { MessageDialogComponent } from './message-dialog/message-dialog.component';
import { MatDialogModule } from '@angular/material/dialog';
import { MyCoursesComponent } from './my-courses/my-courses.component';
import { CourseModalComponent } from './course-modal/course-modal.component';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { QuestionItemComponent } from './question-item/question-item.component';
import { MatRadioModule } from '@angular/material/radio';
import { MatPaginatorModule } from '@angular/material/paginator';
import { CourseScheduleItemComponent } from './course-schedule-item/course-schedule-item.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { QRCodeModule } from 'angular2-qrcode';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { TeacherSignupComponent } from './teacher-signup/teacher-signup.component';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { SettingsModalComponent } from './settings-modal/settings-modal.component';
import { TeacherCardComponent } from './teacher-card/teacher-card.component';
import { MatCardModule } from '@angular/material/card';
import { TeacherPageComponent } from './teacher-page/teacher-page.component';
import { ProfileModalComponent } from './profile-modal/profile-modal.component';
import { ClassroomModalComponent } from './classroom-modal/classroom-modal.component';

@NgModule({
  declarations: [
    AppComponent,
    UserLoginComponent,
    StudentSignupComponent,
    ActivateProfileComponent,
    HomeComponent,
    TopBarComponent,
    CourseCardComponent,
    CarouselComponent,
    CarouselItemComponent,
    CoursesComponent,
    CourseDetailComponent,
    MessageDialogComponent,
    MyCoursesComponent,
    CourseModalComponent,
    QuestionItemComponent,
    CourseScheduleItemComponent,
    TeacherSignupComponent,
    SettingsModalComponent,
    TeacherCardComponent,
    TeacherPageComponent,
    ProfileModalComponent,
    ClassroomModalComponent,
  ],
  imports: [
    FormsModule,
    HttpClientModule,
    BrowserModule,
    AppRoutingModule,
    NgCeilPipeModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatDialogModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatExpansionModule,
    MatRadioModule,
    MatPaginatorModule,
    MatTooltipModule,
    QRCodeModule,
    MatAutocompleteModule,
    NgxChartsModule,
    MatCardModule
  ],
  providers: [
    { provide: UserHttpService, useClass: UserHttpService }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
