package com.example.pictopresent;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class PredictionActivity extends AppCompatActivity {

    Button btnConnect;
    TextView tvPath, tvMessage, tvResult, tvProbab;
    EditText etIP, etPort;
    String imageFilePath = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_prediction);
        imageFilePath = getIntent().getStringExtra("image_path");
        initilizeViews();
    }

    private void initilizeViews() {
        tvPath = (TextView) findViewById(R.id.tvPath);
        tvMessage = (TextView) findViewById(R.id.tvMessage);
        tvResult = (TextView) findViewById(R.id.tvResult);
        tvProbab = (TextView) findViewById(R.id.tvProbab);
        etIP = (EditText) findViewById(R.id.etIP);
        etPort = (EditText) findViewById(R.id.etPort);
        btnConnect = (Button) findViewById(R.id.btnConnect);
        tvPath.setText(imageFilePath);
    }

    public void connectServer(View view) {
        String ip = etIP.getText().toString();
        String port = etPort.getText().toString();
        String postUrl = "http://" + ip + ":" + port + "/";
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inPreferredConfig = Bitmap.Config.RGB_565;
        Bitmap bitmap = BitmapFactory.decodeFile(imageFilePath, options);
        bitmap.compress(Bitmap.CompressFormat.JPEG, 100, stream);
        byte[] bytes = stream.toByteArray();

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("image", "image.jpg", RequestBody.create(MediaType.parse("image/*jpg"), bytes))
                .build();
        tvMessage.setText("Please wait..");
        postRequest(postUrl, requestBody);
    }

    private void postRequest(String postUrl, RequestBody requestBody) {
        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .build();
        final Request request = new Request.Builder()
                .url(postUrl)
                .post(requestBody)
                .build();
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                call.cancel();
                Log.d("FAIL", e.getMessage());
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        tvMessage.setText("Failed to connect to the server.");
                    }
                });
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            tvMessage.setText("Success..");
                            String jsonData = response.body().string();
                            JSONObject jsonObject = new JSONObject(jsonData);
                            JSONArray nameArray = jsonObject.getJSONArray("predictions");
                            JSONArray probabArray = jsonObject.getJSONArray("probabilities");
                            String names = "";
                            String probabs = "";
                            for(int i=0;i<nameArray.length();i++)
                                names = names + nameArray.get(i).toString() + "\n";
                            for(int i=0;i<probabArray.length();i++)
                                probabs = probabs + probabArray.get(i) + "\n";
                            tvResult.setText(names);
                            tvProbab.setText(probabs);
                        } catch (IOException e) {
                            e.printStackTrace();
                        } catch (JSONException e){
                            e.printStackTrace();
                        }
                    }
                });
            }
        });
    }
}
