import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit {
  @Input() title: string = "";
  @Input() exploreLink: string | undefined;
  static id: number = 0;

  constructor() {
    CarouselComponent.id += 1;
  }

  ngOnInit(): void {
  }

  getId(): number {
    return CarouselComponent.id;
  }

}