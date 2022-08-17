import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { BACKEND_URL } from '../globals';
import { Student, Teacher, User } from '../models';
import { UserDataHttpService } from '../user-data-http.service';
import { UserHttpService } from '../user-http.service';

@Component({
  selector: 'app-profile-modal',
  templateUrl: './profile-modal.component.html',
  styleUrls: ['./profile-modal.component.css']
})
export class ProfileModalComponent implements OnInit {
  user_id: number = -1;
  user: User = { email: '', password: null, nome: '', cognome: '', data_nascita: '', sesso: '' };
  teacher_data: Teacher | undefined;
  student_data: Student | undefined;
  school_input: string = "";
  schools: any[] = [];
  errormessage: string | undefined;

  constructor(
    private http: HttpClient,
    private user_http: UserHttpService,
    private user_data_http: UserDataHttpService,
    private router: Router,
    private dialog: MatDialog
  ) {
    let id = this.user_http.getId();
    if (id !== undefined) 
      this.user_id = id;
    else this.router.navigate(['/login'])
  }

  ngOnInit(): void {
    this.user_data_http.getUserData(this.user_id).subscribe({
      next: (user_data) => {
        this.user = user_data;
      }
    })

    if (this.user_http.isStudent()) {
      this.user_data_http.getStudentData(this.user_id).subscribe({
        next: (data) => {
          this.student_data = data;

          this.http.get(`${BACKEND_URL}/scuole?id=${this.student_data?.id_scuola}`).subscribe({
            next: (d: any) => {
              this.school_input = d[0].denominazione;
            }
          });
        }
      })
    } else {
      this.user_data_http.getTeacherData(this.user_id).subscribe({
        next: (data) => {
          this.teacher_data = data;
        }
      })
    }
  }

  isStudent(): boolean {
    return this.user_http.isStudent();
  }

  isTeacher(): boolean {
    return this.user_http.isTeacher();
  }

  filter_schools(): void {
    this.http.get(`${BACKEND_URL}/scuole?name=${this.school_input.toUpperCase()}&limit=300`).subscribe({
      next: (d: any) => {
        this.schools = d;
      }
    })
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];

    if (file && this.teacher_data) {
      this.teacher_data.immagine_profilo = file;
    }
  }

  update() {
    if (this.isStudent()&& this.student_data) {
      if (this.schools.length == 1) {
        this.student_data.id_scuola = this.schools[0].id;
        this.user_data_http.updateStudentData(this.user, this.student_data).subscribe({
          next: (res) => {
            this.dialog.closeAll();
          }
        })
      } else {
        this.errormessage = "Select a valid school";
      }
    } else {
      this.user_data_http.updateTeacherData(this.user, this.teacher_data).subscribe({
        next: (res) => {
          this.dialog.closeAll();
        }
      })
    }
  }
}
