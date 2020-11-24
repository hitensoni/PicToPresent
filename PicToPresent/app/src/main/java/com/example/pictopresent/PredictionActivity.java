package com.example.pictopresent;

import androidx.appcompat.app.AppCompatActivity;

import android.net.Uri;
import android.os.Bundle;
import android.widget.ImageView;

public class PredictionActivity extends AppCompatActivity {

    ImageView ivImage;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_prediction);
        ivImage = (ImageView) findViewById(R.id.ivImage);
        Uri imageUri = getIntent().getParcelableExtra("image_uri");
        ivImage.setImageURI(imageUri);
    }
}
