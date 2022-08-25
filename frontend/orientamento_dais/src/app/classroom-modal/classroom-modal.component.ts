import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AulaHttpService } from '../aula-http.service';
import { Aula } from '../models';

@Component({
  selector: 'app-classroom-modal',
  templateUrl: './classroom-modal.component.html',
  styleUrls: ['./classroom-modal.component.css']
})
export class ClassroomModalComponent implements OnInit {
  aule: Aula[] = []
  new_aule: Aula[] = []
  canSave = false;

  constructor(
    private aula_http: AulaHttpService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.aula_http.getAule().subscribe({
      next: aule => {
        this.aule = aule;
      }
    })
  }

  addAula(): void {
    this.new_aule.push({} as Aula);
    this.canSave = true;
  }

  save() {
    this.new_aule.forEach(aula => {
      this.aula_http.addAula(aula).subscribe({
        next: res => {
          this.dialog.closeAll();
        }
      })
    })
  }
}
