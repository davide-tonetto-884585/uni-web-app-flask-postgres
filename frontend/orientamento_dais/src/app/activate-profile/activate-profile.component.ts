import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { BACKEND_URL } from '../globals';

@Component({
  selector: 'app-activate-profile',
  templateUrl: './activate-profile.component.html',
  styleUrls: ['./activate-profile.component.css']
})
export class ActivateProfileComponent implements OnInit {
  private activation_token: any;
  private user_id: any;
  category: any;
  user_data: any = {};
  errormessage: string | undefined;
  schools: any = [];
  school_input: string = "";

  constructor(
    private user_http: UserHttpService,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.activation_token = params.get('token');
      this.user_id = params.get('user_id');
      this.category = params.get('category');
    });
  }

  complete_registration(): void {
    if (this.schools.length == 1) {
      this.user_data['id_scuola'] = this.schools[0].id;
      this.user_http.completeRegistration(this.user_id, this.activation_token, this.user_data).subscribe({
        next: (d) => {
          this.router.navigate(['/login']);
        },
        error: (err) => {
          console.log('Activation error: ' + JSON.stringify(err));
          this.errormessage = err.error.errormessage;
        }
      })
    } else {
      this.errormessage = "Select a valid school";
    }
  }

  complete_teacher_registration(): void {
    this.user_http.completeTeacherRegistration(this.user_id, this.activation_token, this.user_data).subscribe({
      next: (d) => {
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.log('Activation error: ' + JSON.stringify(err));
        this.errormessage = err.error.errormessage;
      }
    })
  }

  filter_schools(): void {
    this.http.get(`${BACKEND_URL}/scuole?name=${this.school_input.toUpperCase()}&limit=300`).subscribe({
      next: (d) => {
        this.schools = d;
      }
    })
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];

    if (file) {
      this.user_data.immagine_profilo = file;
    }
  }
}
