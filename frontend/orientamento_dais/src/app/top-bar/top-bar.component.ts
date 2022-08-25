import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { SettingsModalComponent } from '../settings-modal/settings-modal.component';
import { ProfileModalComponent } from '../profile-modal/profile-modal.component';
import { ClassroomModalComponent } from '../classroom-modal/classroom-modal.component';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.css']
})
export class TopBarComponent implements OnInit {

  constructor(
    private user_http: UserHttpService,
    private router: Router,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
  }

  getUrl(): string {
    return this.router.url;
  }

  isLogged(): boolean {
    return this.user_http.isLogged();
  }

  getName(): string | boolean {
    return this.user_http.getName();
  }

  logout(): void {
    this.user_http.logout();
    this.router.navigate(['/home']);
  }

  isStudent(): boolean {
    return this.user_http.isStudent();
  }

  isTeacher(): boolean {
    return this.user_http.isTeacher();
  }

  isAdmin(): boolean {
    return this.user_http.isAdmin();
  }

  openSettings(): void {
    const dialog = this.dialog.open(SettingsModalComponent);
  }

  openProfileModal() {
    const dialog = this.dialog.open(ProfileModalComponent);
  }

  openClassroomsModal() {
    const dialog = this.dialog.open(ClassroomModalComponent);
  }
}
